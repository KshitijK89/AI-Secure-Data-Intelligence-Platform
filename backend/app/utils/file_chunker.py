from typing import Iterator, BinaryIO
import os


class FileChunker:
    """
    Efficiently handles large files by processing them in chunks
    """
    
    def __init__(self, max_chunk_size: int = 5 * 1024 * 1024):  # 5MB default
        self.max_chunk_size = max_chunk_size
    
    def chunk_text(self, text: str, chunk_size: int = None) -> Iterator[str]:
        """
        Split text into chunks by lines to preserve context
        """
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        lines = text.split('\n')
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line.encode('utf-8'))
            
            # If adding this line exceeds chunk size and we have content, yield current chunk
            if current_size + line_size > chunk_size and current_chunk:
                yield '\n'.join(current_chunk)
                current_chunk = []
                current_size = 0
            
            current_chunk.append(line)
            current_size += line_size
        
        # Yield remaining chunk
        if current_chunk:
            yield '\n'.join(current_chunk)
    
    def chunk_binary(self, file_obj: BinaryIO, chunk_size: int = None) -> Iterator[bytes]:
        """
        Read binary file in chunks
        """
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        while True:
            chunk = file_obj.read(chunk_size)
            if not chunk:
                break
            yield chunk
    
    def should_chunk(self, file_size: int) -> bool:
        """
        Determine if file should be processed in chunks
        """
        # Chunk files larger than 10MB
        return file_size > 10 * 1024 * 1024
    
    def get_chunk_count(self, file_size: int, chunk_size: int = None) -> int:
        """
        Calculate approximate number of chunks
        """
        if chunk_size is None:
            chunk_size = self.max_chunk_size
        
        return (file_size + chunk_size - 1) // chunk_size
    
    async def process_large_file_async(self, content: str, processor_func) -> list:
        """
        Process large file in chunks asynchronously
        """
        all_results = []
        
        for chunk_num, chunk in enumerate(self.chunk_text(content), start=1):
            print(f"Processing chunk {chunk_num}...")
            result = await processor_func(chunk)
            all_results.append(result)
        
        return all_results
    
    def merge_findings(self, chunked_findings: list, line_offset: int = 0) -> list:
        """
        Merge findings from multiple chunks, adjusting line numbers
        Enhanced to handle both list and dict formats
        """
        merged = []
        current_offset = line_offset
        
        for chunk_findings in chunked_findings:
            # Handle both direct list of findings and dict with 'findings' key
            if isinstance(chunk_findings, dict) and 'findings' in chunk_findings:
                findings = chunk_findings['findings']
                # Adjust line numbers
                for finding in findings:
                    if 'line' in finding and finding['line'] > 0:
                        finding['line'] += current_offset
                    merged.append(finding)
                
                # Update offset based on chunk size
                if 'total_lines' in chunk_findings:
                    current_offset += chunk_findings['total_lines']
            elif isinstance(chunk_findings, list):
                # Direct list of findings
                for finding in chunk_findings:
                    if 'line' in finding and finding['line'] > 0:
                        finding['line'] += current_offset
                    merged.append(finding)
            else:
                # Unknown format, just append
                merged.append(chunk_findings)
        
        return merged
