nnoremap <silent> <Plug>(FilterJump) :FilterJump<Return>
nnoremap <silent> <Plug>(FilterJumpLineBackward) :FilterJumpLineBackward<Return>
nnoremap <silent> <Plug>(FilterJumpLineForward) :FilterJumpLineForward<Return>

autocmd BufLeave,BufDelete,BufWipeout FilterJump FilterJumpVimExit
"autocmd BufDelete,BufWipeout FilterJump FilterJumpVimExit

if !hlexists("SearchCurrent")
    highlight! link SearchCurrent Search
endif
if !hlexists("SearchHighlights")
    highlight! link SearchHighlights IncSearch
endif

