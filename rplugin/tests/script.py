# from pynvim import attach
# nvim = attach('socket', path='/tmp/nvim')

# handle = nvim.request("nvim_create_buf",1,0)
# nvim.request("nvim_open_win",2,True,{'relative':'win','width':50,'height':3,'row':3,'col':3})
# maybe get current window's config and based on it? but resizing will make things weird, like fzf
# src = nvim.new_highlight_source()
buf = nvim.current.buffer
# # for i in range(5):
    # # # has async parameter
    # # buf.add_highlight("String",i,0,-1,src_id=src)
# # # some time later ...
# # buf.clear_namespace(src)
# nvim.command("silent split")
# nvim.command("silent e FilterJump")
# nvim.command("silent setlocal buftype=nofile")
# nvim.command('silent setlocal filetype=FilterJump')
# nvim.current.window.height = 1
# nvim.command("silent CocDisable")
# nvim.command("startinsert")
