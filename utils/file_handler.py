import os
import re
import pandas as pd
from werkzeug.utils import secure_filename

class FileHandler:
    """
    Handle file uploads and email extraction for bulk email processing.
    """
    
    def __init__(self):
        """
        Initialize FileHandler with allowed file types and settings.
        """
        self.allowed_extensions = {'csv', 'xlsx', 'xls', 'txt'}
        self.max_file_size = 16 * 1024 * 1024  # 16MB
        self.max_emails = 1000  # Maximum emails to process
        
    def allowed_file(self, filename):
        """
        Check if uploaded file has allowed extension.
        
        Args:
            filename (str): Name of the uploaded file
            
        Returns:
            bool: True if file type is allowed
        """
        if not filename:
            return False
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def validate_file_size(self, file):
        """
        Validate file size.
        
        Args:
            file: Uploaded file object
            
        Returns:
            bool: True if file size is acceptable
        """
        try:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)  # Reset file pointer
            return size <= self.max_file_size
        except:
            return False
    
    def process_bulk_file(self, file):
        """
        Process uploaded file and extract email addresses.
        
        Args:
            file: Uploaded file object from Flask request
            
        Returns:
            list: List of valid email addresses
            
        Raises:
            ValueError: If file format is invalid or no emails found
        """
        if not file or not file.filename:
            raise ValueError("No file uploaded.")
        
        if not self.allowed_file(file.filename):
            raise ValueError("Invalid file format. Please upload CSV, Excel, or TXT files only.")
        
        if not self.validate_file_size(file):
            raise ValueError(f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB.")
        
        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            raise ValueError("Invalid filename.")
        
        # Create uploads directory if it doesn't exist
        upload_dir = 'static/uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file temporarily
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        try:
            emails = []
            file_extension = filename.rsplit('.', 1)[1].lower()
            
            if file_extension == 'csv':
                emails = self._process_csv_file(filepath)
            elif file_extension in ['xlsx', 'xls']:
                emails = self._process_excel_file(filepath)
            elif file_extension == 'txt':
                emails = self._process_txt_file(filepath)
            
            # Clean up uploaded file
            self._cleanup_file(filepath)
            
            # Validate and filter emails
            valid_emails = self._validate_and_filter_emails(emails)
            
            if not valid_emails:
                raise ValueError("No valid email addresses found in the uploaded file.")
            
            if len(valid_emails) > self.max_emails:
                raise ValueError(f"Too many emails. Maximum {self.max_emails} emails allowed per upload.")
            
            return valid_emails
            
        except Exception as e:
            # Clean up file in case of error
            self._cleanup_file(filepath)
            if "No valid email addresses found" in str(e) or "Too many emails" in str(e):
                raise e
            else:
                raise ValueError(f"Error processing file: {str(e)}")
    
    def _process_csv_file(self, filepath):
        """
        Process CSV file and extract emails.
        
        Args:
            filepath (str): Path to CSV file
            
        Returns:
            list: List of email addresses
        """
        try:
            # Try different encodings
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(filepath, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError("Unable to read CSV file. Please check file encoding.")
            
            return self._extract_emails_from_dataframe(df)
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty.")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    def _process_excel_file(self, filepath):
        """
        Process Excel file and extract emails.
        
        Args:
            filepath (str): Path to Excel file
            
        Returns:
            list: List of email addresses
        """
        try:
            # Read Excel file
            df = pd.read_excel(filepath, engine='openpyxl')
            return self._extract_emails_from_dataframe(df)
            
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def _process_txt_file(self, filepath):
        """
        Process text file and extract emails.
        
        Args:
            filepath (str): Path to text file
            
        Returns:
            list: List of email addresses
        """
        try:
            emails = []
            encodings = ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    # Extract emails from text using regex
                    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                    found_emails = re.findall(email_pattern, content)
                    
                    if found_emails:
                        emails = found_emails
                        break
                    
                    # If no emails found with regex, try line by line
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and self._is_valid_email_format(line):
                            emails.append(line)
                    
                    if emails:
                        break
                        
                except UnicodeDecodeError:
                    continue
            
            return emails
            
        except Exception as e:
            raise ValueError(f"Error reading text file: {str(e)}")
    
    def _extract_emails_from_dataframe(self, df):
        """
        Extract emails from pandas DataFrame.
        
        Args:
            df (pandas.DataFrame): DataFrame containing email data
            
        Returns:
            list: List of email addresses
        """
        emails = []
        
        # Common email column names to look for
        email_columns = [
            'email', 'Email', 'EMAIL', 'e-mail', 'E-mail', 'e_mail',
            'mail', 'Mail', 'email_address', 'emailaddress', 'EmailAddress'
        ]
        
        # Find email column
        email_col = None
        for col in email_columns:
            if col in df.columns:
                email_col = col
                break
        
        if email_col:
            # Extract emails from identified column
            emails = df[email_col].dropna().astype(str).tolist()
        else:
            # If no email column found, search all columns
            for col in df.columns:
                col_data = df[col].dropna().astype(str).tolist()
                for item in col_data:
                    if self._is_valid_email_format(item):
                        emails.append(item)
        
        # Clean up emails
        cleaned_emails = []
        for email in emails:
            email = str(email).strip()
            if email and email.lower() != 'nan':
                cleaned_emails.append(email)
        
        return cleaned_emails
    
    def _validate_and_filter_emails(self, emails):
        """
        Validate and filter email addresses.
        
        Args:
            emails (list): List of email addresses to validate
            
        Returns:
            list: List of valid, unique email addresses
        """
        valid_emails = []
        seen_emails = set()
        
        for email in emails:
            email = str(email).strip().lower()
            
            # Skip empty, invalid, or duplicate emails
            if (email and 
                email != 'nan' and 
                self._is_valid_email_format(email) and 
                email not in seen_emails):
                
                valid_emails.append(email)
                seen_emails.add(email)
        
        return valid_emails
    
    def _is_valid_email_format(self, email):
        """
        Validate email format using regex.
        
        Args:
            email (str): Email address to validate
            
        Returns:
            bool: True if email format is valid
        """
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip()
        if not email:
            return False
        
        # RFC 5322 compliant email regex (simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        try:
            return re.match(pattern, email) is not None
        except:
            return False
    
    def _cleanup_file(self, filepath):
        """
        Remove temporary file.
        
        Args:
            filepath (str): Path to file to remove
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Warning: Could not remove temporary file {filepath}: {str(e)}")
    
    def get_file_info(self, file):
        """
        Get information about uploaded file.
        
        Args:
            file: Uploaded file object
            
        Returns:
            dict: File information
        """
        try:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)  # Reset file pointer
            
            return {
                'filename': file.filename,
                'size': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'extension': file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else '',
                'is_allowed': self.allowed_file(file.filename),
                'is_size_valid': size <= self.max_file_size
            }
        except Exception as e:
            return {
                'filename': file.filename if file else 'Unknown',
                'error': str(e)
            }
