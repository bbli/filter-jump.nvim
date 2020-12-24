nnoremap <silent> <Plug>(FilterJump) :FilterJump<Return>
nnoremap <silent> <Plug>(FilterJumpLineBackward) :FilterJumpLineBackward<Return>
nnoremap <silent> <Plug>(FilterJumpLineForward) :FilterJumpLineForward<Return>

"autocmd BufDelete,BufWipeout FilterJump FilterJumpExit

if !hlexists("SearchCurrent")
    highlight! link SearchCurrent Search
endif
if !hlexists("SearchHighlights")
    highlight! link SearchHighlights Visual
endif

