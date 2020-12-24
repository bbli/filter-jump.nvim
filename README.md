filter-jump
==========
## Motivation/Usage
I wanted a smooth way to move the cursor that satisfied the following criterion:
1. No typing numbers: As explained in this [video](https://www.youtube.com/watch?v=tSq7yDwS1vM&list=LLfDw9928RXloc-CAvO-h-Kw&index=368), numbers are far away and do not keep your typing "cache-friendly". 
2. Jump actually adds to jumps list: For example, relative movments(i.e `10j`) will not be added to the jumplist. Although absolute movements are, this may force you to type more numbers, which as explained above, is slowww.
3. Better `f` functionality: Vim's normal mode `f` suffers from the following problem . Often times one character is just too imprecise, which will means we have to traverse with `;` 2-4 times before reaching our destination. But because the matching results are not highlighted, it is hard to know exactly how many times we have to press `;`. To continue with our computer science analogy, we are basically traversing at the speed of a linked list, where we are unable to "prefetch" the next memory segment(aka plan our normal mode operation) until we have arrived at the current node(aka match).

Furthermore, the following plugins could not produce the behavior I wanted, for various reasons:
* [EasyMotion](https://github.com/easymotion/vim-easymotion): Causes too much screen bloat/color change + typing of "random" characters. Personally I rather type more characters but have them actually be words in my current document, as this keeps my brain "in the flow"
* [Vim-Sneak]: Doesn't provide me the option of only searching the current line, as I feel that two characters will often have too many results when searching the entire page, and so that's where something like `/` would be better
* [Aerojump](https://github.com/ripxorip/aerojump.nvim): This plugin was probably the closest thing that fit my needs, except too many results/screen bloat would appear as a result of the fuzzy matching
* Built in `/`: On the flip side, `/` forces me to type the word exactly as is, whereas most of the time I didn't care for typing out capital letters or underscores. Also `/` searches the entire file, whereas I just want to jump to a location in the current window size. When this happens, the screen "moves", which I don't want. Finally, this pollutes my search history, which is important for my workflow since I mapped `/` to a fuzzy finder version instead


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
