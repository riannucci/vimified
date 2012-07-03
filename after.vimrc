set tabstop=2 
set textwidth=120
set shiftwidth=2 
set softtabstop=2

" Undo Space to toggle folds, because it screws with Ack.vim.
nunmap <Enter>
vunmap <Enter>

colorscheme molokai 

let g:ackprg="ack-grep -H --nocolor --nogroup --column"

let g:ctrlp_extensions = ['tag', 'buffertag']
