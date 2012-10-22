Bundle "bronson/vim-visual-star-search"
Bundle "AutoTag"
Bundle "ervandew/supertab"
Bundle "othree/xml.vim"

if has("python")
  Bundle "klen/python-mode"
endif

Bundle "MarcWeber/vim-addon-mw-utils"
Bundle "tomtom/tlib_vim"
Bundle "honza/snipmate-snippets"
Bundle "garbas/vim-snipmate"

let g:dwm_map_keys = 0
map <C-N> :call DWM_New()<CR>
map <C-C> :call DWM_Close()<CR>
map <C-Space> :call DWM_Focus()<CR>
map <C-@> :call DWM_Focus()<CR>
" In preparation of mode system
map <C-M> :call DWM_Full()<CR>
map <C-J> <C-W>w
map <C-K> <C-W>W
Bundle "spolu/dwm.vim"

Bundle "a.vim"
