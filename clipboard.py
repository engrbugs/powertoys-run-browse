import subprocess


def copy_to_clipboard(string_to_copy):
    process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, close_fds=True)
    process.communicate(input=string_to_copy.encode())
