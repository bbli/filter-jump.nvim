filter-jump
==========
## Motivation/Usage

## Installation
Use your favorite plugin manager, such as [vim-plug](https://github.com/junegunn/vim-plug):
```
Plug 'bbli/filter-jump' {'do': ':UpdateRemotePlugins'}
```
## Mappings
1. Opening FilterJump
Add a map to `<Plug>(FilterJumpOpen)` in your vimrc. This also exists as a command mode command `:FilterJumpOpen`.(Note there is no default mapping)
```
nmap <leader>jj <Plug>(FilterJumpOpen)
```
2. FilterJump Action Keys
These are the default hotkeys. Add this to your vimrc and change it if you want
```
let g:filter_jump_keymaps = {
    \ "<C-n>" : "FilterJumpNextMatch",
    \ "<C-p>" "FilterJumpPrevMatch",
    \ "<CR>" : "FilterJumpSelect",
    \ "<C-f>" : "FilterJumpSelect",
    \ "<C-c>" : "FilterJumpExit"}
```

## More Customization
### Characters to Ignore
By default, this plugin will just ignore `_` when searching. To change this:
```
let g:filter_jump_strip_characters = ["_","@"]
```
### Setting specific options in the JumpBuffer
* Since the search word is typed in a temporary buffer, there may be some keymaps that you would like to not be triggered in this buffer.(As shown below, you actually can put any command mode command into the list, and they will be called when the JumpBuffer is opened) 
```
let g:filter_jump_buffer_options = ["inoremap <buffer> <C-j> <Nop>"]
```
### Changing the Highlight Coloring
This plugin defines the highlight groups `SearchCurrent` and `SearchHighlights`, and maps them to `Search` and `Visual` highlight groups respectively. If you would like to change that, add something like the following:
```
highlight! link SearchCurrent Red "This assumes you have the Red highlight group defined.
highlight! link SearchHighlights Green
let g:filter_jump_highlight_groups = 1 "This tells the plugin you already defined the highlighting schemes
```
