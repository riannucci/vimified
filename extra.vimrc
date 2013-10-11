Bundle "bronson/vim-visual-star-search"
Bundle "AutoTag"
Bundle "ervandew/supertab"
Bundle "othree/xml.vim"

if has("python")
  Bundle "klen/python-mode"
endif

Bundle "MarcWeber/vim-addon-mw-utils"
Bundle "tomtom/tlib_vim"
Bundle "scrooloose/snipmate-snippets"
Bundle "garbas/vim-snipmate"

Bundle "a.vim"

Bundle "airblade/vim-gitgutter"

Bundle "ehamberg/vim-cute-python"

if !has('win32')
  Bundle "Valloric/YouCompleteMe"
endif

Bundle 'Lokaltog/powerline'
set rtp+=~/.vim/bundle/powerline/powerline/bindings/vim

Bundle 'arsenerei/vim-ragel'
