from tempfile import mktemp
from pathlib import Path
from platform import system, platform
from random import shuffle
os = system()
if os == 'Windows':
    block_size = 0x10000
elif os == 'Linux':
    block_size = 0x2000
else:
    pass

def test_import():
    try:
        result = None
        import sparse_file
    except Exception as e:
        result = e
    assert isinstance(result, RuntimeError) == os not in ('Linux','Windows')

if os in ('Linux','Windows'):
    from sparse_file import open_sparse

    filename = Path(mktemp())

    def test_no_file():
        if filename.exists():
            filename.unlink()
        try:
            result = open_sparse(filename, 'r+')
        except Exception as e:
            result = e
        assert isinstance(result, OSError)

    def test_file_opened_for_read():
        if not filename.exists():
            open(filename,'w').close()
        try:
            result = open_sparse(filename, 'r')
        except Exception as e:
            result = e
        filename.unlink()
        assert isinstance(result, RuntimeError)

    def test_file_closed_then_sized():
        if filename.exists():
            filename.unlink()
        # Open the file. This should succeed wihtout issue
        file = open_sparse(filename, 'w+b')
        # Now close the file.
        file.close()
        # Last, try to get the file's size.
        try:
            result = file.size_on_disk()
        except Exception as e:
            result = e
        assert isinstance(result, RuntimeError)

    def test_file_closed_then_made_sparse():
        if filename.exists():
            filename.unlink()
        # Open the file. This should succeed wihtout issue
        file = open_sparse(filename, 'w+b')
        # Now close the file.
        file.close()
        # Last, try to get the file's size.
        try:
            result = file.hole(0x0, 0x100) # Values don't matter.
        except Exception as e:
            result = e
        assert isinstance(result, RuntimeError)

    def test_file_sparse_operations():
        if filename.exists():
            filename.unlink()
        # Open the file. This should succeed wihtout issue
        file = open_sparse(filename, 'w+b')
        # Calculate the data to write to the file.
        bytes_to_write = block_size * 256
        # Write the file and verify that things work as expected.
        bytes_written = file.write(b'\x01'*bytes_to_write)
        assert bytes_to_write == bytes_written
        # Commit to disk.
        file.flush()
        # Get the current size.
        space_used = file.size_on_disk()
        # Generate a random list of blocks to punch holes out with.
        blocks = list(range(0,bytes_to_write, block_size))
        shuffle(blocks)
        # Begin deallocating from the file.
        for block in blocks:
            # Punch the hole.
            result = file.hole(block, block_size)
            assert result == True
            # Confirm the space was removed.
            stat = filename.stat()
            new_space_used = file.size_on_disk()
            assert new_space_used < space_used
            space_used = new_space_used
        # Cleanup.
        file.close()
        filename.unlink()

    if platform().find('WSL2') != -1:
        def test_wsl_file_sparse_fails():
            wsl_filename = Path(mktemp(dir='/mnt/c/Windows/Temp'))
            if wsl_filename.exists():
                wsl_filename.unlink()
            # Open the file. This should succeed wihtout issue
            file = open_sparse(wsl_filename, 'w+b')
            # Calculate the data to write to the file.
            bytes_to_write = block_size * 256
            # Write the file and verify that things work as expected.
            bytes_written = file.write(b'\x01'*bytes_to_write)
            assert bytes_to_write == bytes_written
            # Commit to disk.
            file.flush()
            # Generate a random list of blocks to punch holes out with.
            blocks = list(range(0,bytes_to_write, block_size))
            shuffle(blocks)
            # Begin deallocating from the file, just one block.
            block = blocks[0]
            # Punch the hole. It should fail.
            try:
                result = file.hole(block, block_size)
            except Exception as e:
                result = e
            assert isinstance(result, OSError)
            # Cleanup.
            file.close()
            wsl_filename.unlink()
