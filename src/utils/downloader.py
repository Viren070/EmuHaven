from requests.exceptions import RequestException


def download_through_stream(response, download_path, progress_frame, chunk_size, total_size=None, custom=True):
    with open(download_path, 'wb') as f:
        downloaded_bytes = 0
        try:
            for chunk in response.iter_content(chunk_size=chunk_size): 
                if custom and progress_frame.cancel_download_raised:
                    progress_frame.destroy()
                    return (False, "Cancelled", download_path)
                f.write(chunk)
                downloaded_bytes += len(chunk)
                if custom:
                    progress_frame.update_download_progress(downloaded_bytes, chunk_size)
                else:
                    progress_frame.set(downloaded_bytes/total_size)
            progress_frame.destroy()
        except RequestException as error:
            progress_frame.destroy()
            return (False, error)
    return (True, download_path)