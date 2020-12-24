nnoremap <silent> <Plug>(FilterJumpOpen) :FilterJumpOpen<Return>
nnoremap <silent> <Plug>(FilterJumpLineBackward) :FilterJumpLineBackward<Return>
nnoremap <silent> <Plug>(FilterJumpLineForward) :FilterJumpLineForward<Return>

if !exists("g:filter_jump_highlight_groups")
    highlight! link SearchCurrent Search
    highlight! link SearchHighlights Visual
endif

