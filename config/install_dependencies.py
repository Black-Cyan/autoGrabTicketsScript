import subprocess


def install_dependencies():
    subprocess.call(['pip', 'install', '-r', 'requirements.txt'])

if __name__ == '__main__':
    install_dependencies()