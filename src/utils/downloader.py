from requests.exceptions import RequestException

def download_through_stream(response, download_path, progress_frame, chunk_size):
    with open(download_path, 'wb') as f:
        downloaded_bytes = 0
        try:
            for chunk in response.iter_content(chunk_size=chunk_size): 
                if progress_frame.cancel_download_raised:
                    progress_frame.destroy()
                    return (False, "Cancelled")
                f.write(chunk)
                downloaded_bytes += len(chunk)
                progress_frame.update_download_progress(downloaded_bytes, chunk_size)
            progress_frame.destroy()
        except RequestException as error:
            return (False, error)
    return (True, download_path)