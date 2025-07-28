"""
Enhanced CSV file processing utilities with advanced splitting features
"""

import os
import re
import math
from src.core.utils import log_message


class CSVProcessor:
    """Enhanced CSV processor with advanced splitting capabilities"""
    
    def __init__(self, output_widget):
        self.output_widget = output_widget
        
    def split_csv_advanced(self, filepath, split_mode="basic", split_params=None, add_line_numbers=True):
        """
        Advanced CSV splitting with multiple modes
        
        Args:
            filepath: Path to CSV file
            split_mode: "basic", "by_id_range", "by_text_length", "by_count", "by_pattern"
            split_params: Dictionary with mode-specific parameters
            add_line_numbers: Whether to add line numbers to text
        """
        try:
            with open(filepath, encoding='utf-8') as f:
                lines = f.readlines()
            
            meta_lines = [line for line in lines if line.startswith(';')]
            data_lines = [line for line in lines if not line.startswith(';')]
            
            # Parse CSV data
            parsed_data = []
            for line in data_lines:
                parts = line.strip().split('|', maxsplit=3)
                if len(parts) == 4:
                    text_id = parts[0]
                    key_hex = parts[1]
                    key_str = parts[2]
                    text_content = parts[3]
                    
                    parsed_data.append({
                        'id': text_id,
                        'key_hex': key_hex,
                        'key_str': key_str,
                        'text': text_content,
                        'id_key_line': f"{text_id}|{key_hex}|{key_str}",
                        'original_line': line.strip()
                    })
            
            if not parsed_data:
                raise Exception("No valid data found in CSV file")
            
            log_message(self.output_widget, f"📊 Parsed {len(parsed_data)} entries from CSV")
            
            # Perform splitting based on mode
            if split_mode == "basic":
                return self._split_basic(filepath, parsed_data, meta_lines, add_line_numbers)
            elif split_mode == "by_id_range":
                return self._split_by_id_range(filepath, parsed_data, meta_lines, split_params, add_line_numbers)
            elif split_mode == "by_text_length":
                return self._split_by_text_length(filepath, parsed_data, meta_lines, split_params, add_line_numbers)
            elif split_mode == "by_count":
                return self._split_by_count(filepath, parsed_data, meta_lines, split_params, add_line_numbers)
            elif split_mode == "by_pattern":
                return self._split_by_pattern(filepath, parsed_data, meta_lines, split_params, add_line_numbers)
            else:
                raise Exception(f"Unknown split mode: {split_mode}")
                
        except Exception as e:
            error_msg = f"Error splitting file: {str(e)}"
            log_message(self.output_widget, f"✗ {error_msg}")
            return False, None, None
    
    def _split_basic(self, filepath, parsed_data, meta_lines, add_line_numbers):
        """Basic split into ID/Key and Text files"""
        base_name = os.path.splitext(filepath)[0]
        idkey_path = base_name + "_idkey.csv"
        text_path = base_name + ("_text_with_id.txt" if add_line_numbers else "_text_id_separated.txt")
        
        # Save ID/Key file
        with open(idkey_path, 'w', encoding='utf-8') as f:
            for meta in meta_lines:
                f.write(meta)
            for entry in parsed_data:
                f.write(entry['id_key_line'] + '\n')
        
        # Save Text file
        with open(text_path, 'w', encoding='utf-8') as f:
            for entry in parsed_data:
                if add_line_numbers:
                    f.write(f"{entry['id']}:{entry['text']}\n")
                else:
                    f.write(f"{entry['id']}|{entry['text']}\n")
        
        log_message(self.output_widget, f"✓ Basic split completed!")
        log_message(self.output_widget, f"📄 ID/Key file: {idkey_path}")
        log_message(self.output_widget, f"📄 Text file: {text_path}")
        
        return True, (idkey_path, text_path), os.path.dirname(filepath)
    
    def _split_by_id_range(self, filepath, parsed_data, meta_lines, split_params, add_line_numbers):
        """Split by ID ranges (fixed logic)"""
        range_size = split_params.get('range_size', 500)
        max_files = split_params.get('max_files', 10)
        
        # Try to convert IDs to integers for numeric sorting
        numeric_data = []
        text_data = []
        
        for entry in parsed_data:
            try:
                numeric_id = int(entry['id'])
                numeric_data.append((numeric_id, entry))
            except ValueError:
                text_data.append(entry)
        
        # Sort numeric IDs
        numeric_data.sort(key=lambda x: x[0])
        
        base_name = os.path.splitext(filepath)[0]
        created_files = []
        
        log_message(self.output_widget, f"🔢 Splitting by ID ranges (size: {range_size})")
        log_message(self.output_widget, f"📊 Found {len(numeric_data)} numeric IDs, {len(text_data)} text IDs")
        
        # Create single ID/Key file
        idkey_path = base_name + "_idkey.csv"
        with open(idkey_path, 'w', encoding='utf-8') as f:
            for meta in meta_lines:
                f.write(meta)
            for _, entry in numeric_data:
                f.write(entry['id_key_line'] + '\n')
            for entry in text_data:
                f.write(entry['id_key_line'] + '\n')
        
        created_files.append(idkey_path)
        
        # NEW LOGIC: Split by entry count, not by ID value gaps
        if numeric_data:
            total_entries = len(numeric_data)
            file_count = 0
            
            # Split into chunks by entry count
            for i in range(0, total_entries, range_size):
                if file_count >= max_files:
                    break
                    
                # Get chunk of entries
                chunk_end = min(i + range_size, total_entries)
                chunk_entries = [entry for _, entry in numeric_data[i:chunk_end]]
                
                if chunk_entries:
                    # Get actual ID range for this chunk
                    start_id = numeric_data[i][0]
                    end_id = numeric_data[chunk_end - 1][0]
                    
                    # Create text file for this chunk
                    text_path = f"{base_name}_text_range_{start_id}-{end_id}_entries{i+1}-{chunk_end}.txt"
                    with open(text_path, 'w', encoding='utf-8') as f:
                        for entry in chunk_entries:
                            if add_line_numbers:
                                f.write(f"{entry['id']}:{entry['text']}\n")
                            else:
                                f.write(f"{entry['id']}|{entry['text']}\n")
                    
                    created_files.append(text_path)
                    log_message(self.output_widget, f"📄 Created: {os.path.basename(text_path)} ({len(chunk_entries)} entries)")
                    log_message(self.output_widget, f"   ID range: {start_id} to {end_id}")
                
                file_count += 1
        
        # Create separate file for text IDs if any
        if text_data:
            text_path = f"{base_name}_text_non_numeric.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                for entry in text_data:
                    if add_line_numbers:
                        f.write(f"{entry['id']}:{entry['text']}\n")
                    else:
                        f.write(f"{entry['id']}|{entry['text']}\n")
            
            created_files.append(text_path)
            log_message(self.output_widget, f"📄 Created: {os.path.basename(text_path)} ({len(text_data)} non-numeric IDs)")
        
        log_message(self.output_widget, f"✓ ID range split completed! Created {len(created_files)} files")
        log_message(self.output_widget, f"ℹ Note: Split by entry count ({range_size} entries/file), not by ID value gaps")
        return True, created_files, os.path.dirname(filepath)
    
    def _split_by_text_length(self, filepath, parsed_data, meta_lines, split_params, add_line_numbers):
        """Split by text length"""
        length_threshold = split_params.get('length_threshold', 200)
        
        short_texts = []
        long_texts = []
        
        for entry in parsed_data:
            text_length = len(entry['text'])
            if text_length >= length_threshold:
                long_texts.append(entry)
            else:
                short_texts.append(entry)
        
        base_name = os.path.splitext(filepath)[0]
        created_files = []
        
        log_message(self.output_widget, f"📏 Splitting by text length (threshold: {length_threshold} chars)")
        log_message(self.output_widget, f"📊 Long texts: {len(long_texts)}, Short texts: {len(short_texts)}")
        
        # Create single ID/Key file
        idkey_path = base_name + "_idkey.csv"
        with open(idkey_path, 'w', encoding='utf-8') as f:
            for meta in meta_lines:
                f.write(meta)
            for entry in parsed_data:
                f.write(entry['id_key_line'] + '\n')
        
        created_files.append(idkey_path)
        
        # Create file for long texts
        if long_texts:
            long_text_path = f"{base_name}_text_long_{length_threshold}plus.txt"
            with open(long_text_path, 'w', encoding='utf-8') as f:
                for entry in long_texts:
                    if add_line_numbers:
                        f.write(f"{entry['id']}:{entry['text']}\n")
                    else:
                        f.write(f"{entry['id']}|{entry['text']}\n")
            
            created_files.append(long_text_path)
            log_message(self.output_widget, f"📄 Created: {os.path.basename(long_text_path)} ({len(long_texts)} long texts)")
        
        # Create file for short texts
        if short_texts:
            short_text_path = f"{base_name}_text_short_under{length_threshold}.txt"
            with open(short_text_path, 'w', encoding='utf-8') as f:
                for entry in short_texts:
                    if add_line_numbers:
                        f.write(f"{entry['id']}:{entry['text']}\n")
                    else:
                        f.write(f"{entry['id']}|{entry['text']}\n")
            
            created_files.append(short_text_path)
            log_message(self.output_widget, f"📄 Created: {os.path.basename(short_text_path)} ({len(short_texts)} short texts)")
        
        log_message(self.output_widget, f"✓ Text length split completed! Created {len(created_files)} files")
        return True, created_files, os.path.dirname(filepath)
    
    def _split_by_count(self, filepath, parsed_data, meta_lines, split_params, add_line_numbers):
        """Split by entry count per file"""
        entries_per_file = split_params.get('entries_per_file', 100)
        
        base_name = os.path.splitext(filepath)[0]
        created_files = []
        
        total_entries = len(parsed_data)
        num_files = math.ceil(total_entries / entries_per_file)
        
        log_message(self.output_widget, f"🔢 Splitting by count ({entries_per_file} entries per file)")
        log_message(self.output_widget, f"📊 Total entries: {total_entries}, Will create: {num_files} text files")
        
        # Create single ID/Key file
        idkey_path = base_name + "_idkey.csv"
        with open(idkey_path, 'w', encoding='utf-8') as f:
            for meta in meta_lines:
                f.write(meta)
            for entry in parsed_data:
                f.write(entry['id_key_line'] + '\n')
        
        created_files.append(idkey_path)
        
        # Create text files by count
        for i in range(num_files):
            start_idx = i * entries_per_file
            end_idx = min(start_idx + entries_per_file, total_entries)
            
            file_entries = parsed_data[start_idx:end_idx]
            
            text_path = f"{base_name}_text_part{i+1:03d}_entries{start_idx+1}-{end_idx}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                for entry in file_entries:
                    if add_line_numbers:
                        f.write(f"{entry['id']}:{entry['text']}\n")
                    else:
                        f.write(f"{entry['id']}|{entry['text']}\n")
            
            created_files.append(text_path)
            log_message(self.output_widget, f"📄 Created: {os.path.basename(text_path)} ({len(file_entries)} entries)")
        
        log_message(self.output_widget, f"✓ Count-based split completed! Created {len(created_files)} files")
        return True, created_files, os.path.dirname(filepath)
    
    def _split_by_pattern(self, filepath, parsed_data, meta_lines, split_params, add_line_numbers):
        """Split by text pattern matching"""
        pattern = split_params.get('pattern', '')
        pattern_name = split_params.get('pattern_name', 'pattern')
        case_sensitive = split_params.get('case_sensitive', False)
        
        if not pattern:
            raise Exception("Pattern is required for pattern-based splitting")
        
        # Compile regex pattern
        regex_flags = 0 if case_sensitive else re.IGNORECASE
        try:
            compiled_pattern = re.compile(pattern, regex_flags)
        except re.error as e:
            raise Exception(f"Invalid regex pattern: {e}")
        
        matching_entries = []
        non_matching_entries = []
        
        for entry in parsed_data:
            if compiled_pattern.search(entry['text']):
                matching_entries.append(entry)
            else:
                non_matching_entries.append(entry)
        
        base_name = os.path.splitext(filepath)[0]
        created_files = []
        
        log_message(self.output_widget, f"🔍 Splitting by pattern: '{pattern}'")
        log_message(self.output_widget, f"📊 Matching: {len(matching_entries)}, Non-matching: {len(non_matching_entries)}")
        
        # Create single ID/Key file
        idkey_path = base_name + "_idkey.csv"
        with open(idkey_path, 'w', encoding='utf-8') as f:
            for meta in meta_lines:
                f.write(meta)
            for entry in parsed_data:
                f.write(entry['id_key_line'] + '\n')
        
        created_files.append(idkey_path)
        
        # Create file for matching entries
        if matching_entries:
            matching_path = f"{base_name}_text_matching_{pattern_name}.txt"
            with open(matching_path, 'w', encoding='utf-8') as f:
                for entry in matching_entries:
                    if add_line_numbers:
                        f.write(f"{entry['id']}:{entry['text']}\n")
                    else:
                        f.write(f"{entry['id']}|{entry['text']}\n")
            
            created_files.append(matching_path)
            log_message(self.output_widget, f"📄 Created: {os.path.basename(matching_path)} ({len(matching_entries)} matching)")
        
        # Create file for non-matching entries
        if non_matching_entries:
            non_matching_path = f"{base_name}_text_non_matching_{pattern_name}.txt"
            with open(non_matching_path, 'w', encoding='utf-8') as f:
                for entry in non_matching_entries:
                    if add_line_numbers:
                        f.write(f"{entry['id']}:{entry['text']}\n")
                    else:
                        f.write(f"{entry['id']}|{entry['text']}\n")
            
            created_files.append(non_matching_path)
            log_message(self.output_widget, f"📄 Created: {os.path.basename(non_matching_path)} ({len(non_matching_entries)} non-matching)")
        
        log_message(self.output_widget, f"✓ Pattern-based split completed! Created {len(created_files)} files")
        return True, created_files, os.path.dirname(filepath)
    
    def merge_csv_with_priority(self, idkey_files, text_files, smart_merge=True):
        """
        Merge multiple ID/Key files and Text files with priority-based conflict resolution
        
        Args:
            idkey_files: List of ID/Key file paths
            text_files: List of text file paths (ordered by priority - first = highest priority)
            smart_merge: Auto-detect text format
        """
        try:
            # Collect all ID/Key data with priority tracking
            all_idkey_data = {}
            
            log_message(self.output_widget, f"🔄 Processing {len(idkey_files)} ID/Key files...")
            
            for file_idx, idkey_file in enumerate(idkey_files):
                with open(idkey_file, encoding='utf-8') as f:
                    lines = f.readlines()
                
                meta_lines = [line for line in lines if line.startswith(';')]
                data_lines = [line for line in lines if not line.startswith(';')]
                
                # Save metadata from the first file
                if file_idx == 0:
                    master_meta = meta_lines
                
                for line in data_lines:
                    parts = line.strip().split('|', maxsplit=2)
                    if len(parts) >= 1:
                        text_id = parts[0]
                        
                        if text_id in all_idkey_data:
                            # ID already exists, keep the higher priority file (first file)
                            log_message(self.output_widget, 
                                f"⚠ Duplicate ID {text_id} in ID/Key files, keeping the first file")
                        else:
                            all_idkey_data[text_id] = {
                                'data': line.strip(),
                                'source_file': os.path.basename(idkey_file),
                                'priority': file_idx
                            }
            
            # Collect all text data with priority tracking
            all_text_data = {}
            
            log_message(self.output_widget, f"🔄 Processing {len(text_files)} Text files with priority...")
            
            for file_idx, text_file in enumerate(text_files):
                log_message(self.output_widget, f"  [{file_idx+1}] Processing {os.path.basename(text_file)}")
                
                with open(text_file, encoding='utf-8') as f:
                    text_lines = [line.rstrip('\n\r') for line in f.readlines()]
                
                for line in text_lines:
                    if not line.strip():
                        continue
                        
                    text_id = None
                    text_content = ""
                    
                    if smart_merge:
                        # Try format ID:content
                        match = re.match(r'^([^:]+):(.*)', line)
                        if match:
                            text_id = match.group(1)
                            text_content = match.group(2)
                        else:
                            # Try format ID|content
                            parts = line.split('|', 1)
                            if len(parts) == 2:
                                text_id = parts[0]
                                text_content = parts[1]
                    else:
                        # Only use format ID|content
                        parts = line.split('|', 1)
                        if len(parts) == 2:
                            text_id = parts[0]
                            text_content = parts[1]
                    
                    if text_id:
                        if text_id in all_text_data:
                            # ID already exists, check priority
                            existing_priority = all_text_data[text_id]['priority']
                            if file_idx < existing_priority:
                                # Current file has higher priority, replace
                                log_message(self.output_widget, 
                                    f"🔄 ID {text_id}: Replaced by higher priority file [{file_idx+1}]")
                                all_text_data[text_id] = {
                                    'content': text_content,
                                    'source_file': os.path.basename(text_file),
                                    'priority': file_idx
                                }
                            else:
                                # Current file has lower priority, skip
                                log_message(self.output_widget, 
                                    f"⏭ ID {text_id}: Skipped due to lower priority")
                        else:
                            # New ID, add
                            all_text_data[text_id] = {
                                'content': text_content,
                                'source_file': os.path.basename(text_file),
                                'priority': file_idx
                            }
            
            # Create merged data
            merged_lines = []
            processed_ids = set()
            
            # Priority for IDs with both key and text
            for text_id in all_idkey_data:
                if text_id in all_text_data:
                    idkey_data = all_idkey_data[text_id]['data']
                    text_content = all_text_data[text_id]['content']
                    merged_line = idkey_data + '|' + text_content
                    merged_lines.append(merged_line)
                    processed_ids.add(text_id)
            
            # Add IDs with only key (no text)
            for text_id in all_idkey_data:
                if text_id not in processed_ids:
                    idkey_data = all_idkey_data[text_id]['data']
                    merged_line = idkey_data + '|'  # Empty text
                    merged_lines.append(merged_line)
                    processed_ids.add(text_id)
            
            # Detailed result report
            matched_count = sum(1 for tid in all_idkey_data if tid in all_text_data)
            orphaned_keys = len(all_idkey_data) - matched_count
            orphaned_texts = len(all_text_data) - matched_count
            
            log_message(self.output_widget, f"📊 Merge result:")
            log_message(self.output_widget, f"  - {matched_count} IDs with both key and text")
            log_message(self.output_widget, f"  - {orphaned_keys} IDs with only key (empty text)")
            log_message(self.output_widget, f"  - {orphaned_texts} IDs with only text (skipped)")
            
            # Statistics by source file
            log_message(self.output_widget, f"📈 Text source statistics:")
            text_source_stats = {}
            for text_id, data in all_text_data.items():
                if text_id in all_idkey_data:  # Only count used text
                    source = data['source_file']
                    text_source_stats[source] = text_source_stats.get(source, 0) + 1
            
            for source, count in text_source_stats.items():
                log_message(self.output_widget, f"  - {source}: {count} text entries")
            
            # Create output file
            output_path = self._generate_output_path(idkey_files[0])
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write metadata
                if 'master_meta' in locals():
                    for meta in master_meta:
                        f.write(meta)
                
                # Write merged data
                for line in merged_lines:
                    f.write(line + '\n')
            
            log_message(self.output_widget, f"✓ Merge successful with priority order!")
            log_message(self.output_widget, f"Result file: {output_path}")
            
            return True, output_path, os.path.dirname(output_path)
            
        except Exception as e:
            error_msg = f"Error merging files: {str(e)}"
            log_message(self.output_widget, f"✗ {error_msg}")
            return False, None, None
    
    def _generate_output_path(self, first_idkey_file):
        """Generate output file path"""
        base_name = os.path.splitext(first_idkey_file)[0]
        # Remove _idkey suffix if present
        if base_name.endswith('_idkey'):
            base_name = base_name[:-6]
        
        return base_name + "_merged.csv"
    
    def split_csv(self, filepath, add_line_numbers=True):
        """
        Legacy method for backward compatibility
        """
        return self.split_csv_advanced(filepath, "basic", None, add_line_numbers)