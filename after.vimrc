set tabstop=2 
set textwidth=120
set shiftwidth=2 
set softtabstop=2

" Stop the crazy margins :D
set numberwidth=2

" More useful than not
set ignorecase

" Undo Space to toggle folds, because it screws with Ack.vim.
nunmap <Enter>
vunmap <Enter>

colorscheme molokai 

let g:ackprg="ack-grep -H --nocolor --nogroup --column"

let g:ctrlp_extensions = ['tag', 'buffertag']
