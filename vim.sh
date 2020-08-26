mkdir ~/vim
cd ~/vim

curl 'https://s3.amazonaws.com/bengoa/vim-static.tar.gz' | tar -xz

export VIMRUNTIME="$HOME/vim/runtime"
export PATH="$HOME/vim:$PATH"
cd -