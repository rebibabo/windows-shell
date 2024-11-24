import os
import argparse
import requests
from dataclasses import dataclass
from prompt_toolkit import HTML, print_formatted_text
from cmds.base import Command

normabs = lambda x: os.path.normpath(os.path.abspath(x.replace('~', os.path.expanduser('~'))))

@dataclass
class WgetCommand(Command):
    def __init__(self, command: str) -> 'WgetCommand':
        """
        解析 wget 命令并返回 WgetCommand 实例。
        """
        parser = argparse.ArgumentParser(description="Download files from the web.", add_help=False)
        parser.add_argument("-O", "--output-document", type=str, help="Write documents to the specified file.")
        parser.add_argument("-q", "--quiet", action="store_true", help="Turn off output messages.")
        parser.add_argument("-v", "--verbose", action="store_true", help="Print detailed output (default).")
        parser.add_argument("-c", "--continue", action="store_true", dest="continue_", help="Resume a partially downloaded file.")
        parser.add_argument("url", type=str, help="URL to download the file from.")
        
        self.parser = parser
        super().__init__(command)

    @Command.safe_exec
    def execute(self):
        url = self.url
        output_path = normabs(self.output_document or os.path.basename(url))
        
        if not url:
            print_formatted_text(HTML("<error>Error: No URL specified.</error>"), style=self.log_style)
            return

        try:
            headers = {}
            # 检查是否需要续传
            if self.continue_ and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                headers['Range'] = f'bytes={file_size}-'
                if not self.quiet:
                    print(f"Resuming download for '{output_path}' from byte {file_size}.")
            else:
                file_size = 0
            
            # 发起请求
            with requests.get(url, headers=headers, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get('Content-Length', 0)) + file_size
                mode = 'ab' if self.continue_ else 'wb'

                with open(output_path, mode) as file:
                    downloaded = file_size
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            if self.verbose and not self.quiet:
                                print(f"\rDownloading... {downloaded}/{total_size} bytes", end="\r")
                    
                    if self.verbose and not self.quiet:
                        print("\nDownload completed.")

        except requests.exceptions.RequestException as e:
            print_formatted_text(HTML(f"<critical>Critical Error: Failed to download '{url}': {e}</critical>"), style=self.log_style)
        except Exception as e:
            print_formatted_text(HTML(f"<error>Error: {e}</error>"), style=self.log_style)

# 示例用法
if __name__ == "__main__":
    command = "-O example.html -c https://github.com/prompt-toolkit/python-prompt-toolkit.git"  # 示例命令
    wget_command = WgetCommand(command)
    wget_command.execute()
