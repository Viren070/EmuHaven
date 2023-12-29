from requests.exceptions import RequestException

def download_through_stream(response, download_path, progress_frame, chunk_size):
    with open(download_path, 'wb') as f:
        downloaded_bytes = 0
        try:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if progress_frame.cancel_download_raised:
                    progress_frame.grid_forget()
                    return (False, "Cancelled", download_path)
                f.write(chunk)
                downloaded_bytes += len(chunk)

                progress_frame.update_download_progress(downloaded_bytes)

            progress_frame.complete_download()
        except RequestException as error:
            progress_frame.grid_forget()
            return (False, error)
    return (True, download_path)

def download_file(response, download_path):
    try:
        response.raise_for_status()
        with open(download_path, 'wb') as f:
            f.write(response.content)
        return (True, download_path)
    except RequestException as error:
        return (False, error)
    