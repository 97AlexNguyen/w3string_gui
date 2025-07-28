"""
Command handler for executing w3strings.exe commands
"""

import os
import subprocess
from src.core.utils import log_message, validate_file_extension
from src.core.constants import VERBOSE_NONE, VERBOSE_NORMAL, VERBOSE_VERY


class CommandHandler:
    """Handles building and executing w3strings commands"""
    
    def __init__(self, w3strings_path):
        self.w3strings_path = w3strings_path
        
    def build_decode_command(self, file_path, verbose_option):
        """Build decode command"""
        cmd = [str(self.w3strings_path), "-d", file_path]
        return self._add_verbose_options(cmd, verbose_option)
        
    def build_encode_command(self, file_path, verbose_option, id_space=None, force_ignore=False):
        """Build encode command"""
        cmd = [str(self.w3strings_path), "-e", file_path]
        
        # Add ID space if provided
        if id_space and id_space.strip():
            cmd.extend(["-i", id_space.strip()])
            
        # Add force ignore option
        if force_ignore:
            cmd.append("--force-ignore-id-space-check-i-know-what-i-am-doing")
            
        return self._add_verbose_options(cmd, verbose_option)
        
    def _add_verbose_options(self, cmd, verbose_option):
        """Add verbose options to command"""
        if verbose_option == VERBOSE_NORMAL:
            cmd.append("-v")
        elif verbose_option == VERBOSE_VERY:
            cmd.append("--very-verbose")
        return cmd
        
    def execute_command(self, cmd, output_widget):
        """Execute command and log output"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.stdout:
                log_message(output_widget, f"Output: {result.stdout}")
            if result.stderr:
                log_message(output_widget, f"Error: {result.stderr}")
                
            if result.returncode == 0:
                log_message(output_widget, "✓ Command executed successfully")
            else:
                log_message(output_widget, f"✗ Command failed with return code {result.returncode}")
                
            return result.returncode == 0
            
        except Exception as e:
            log_message(output_widget, f"Exception: {str(e)}")
            return False
            
    def process_files(self, action, file_list, verbose_option, output_widget, 
                     id_space=None, force_ignore=False):
        """Process multiple files with the specified action"""
        if not file_list:
            return False, "No files selected"
            
        if not self.w3strings_path.exists():
            return False, f"w3strings.exe not found at: {self.w3strings_path}"
            
        # Clear output
        output_widget.delete(1.0, 'end')
        
        success_count = 0
        total_files = len(file_list)
        output_folders = set()
        
        for i, file_path in enumerate(file_list, 1):
            log_message(output_widget, f"[{i}/{total_files}] Processing: {os.path.basename(file_path)}")
            
            # Validate file extension
            if action == "decode" and not validate_file_extension(file_path, '.w3strings'):
                log_message(output_widget, f"⚠ Warning: {file_path} is not a .w3strings file")
            elif action == "encode" and not validate_file_extension(file_path, '.csv'):
                log_message(output_widget, f"⚠ Warning: {file_path} is not a .csv file")
                
            # Build appropriate command
            if action == "decode":
                cmd = self.build_decode_command(file_path, verbose_option)
            else:  # encode
                cmd = self.build_encode_command(file_path, verbose_option, id_space, force_ignore)
                
            log_message(output_widget, f"Command: {' '.join(cmd)}")
            
            if self.execute_command(cmd, output_widget):
                success_count += 1
                output_folders.add(os.path.dirname(file_path))
                
            log_message(output_widget, "-" * 50)
            
        log_message(output_widget, f"Completed: {success_count}/{total_files} files processed successfully")
        
        return success_count > 0, list(output_folders)[0] if output_folders else None