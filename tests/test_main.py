from snowleopard.cli import main


def test_main_no_args(capsys):
    """Test that main function prints help when no command is given."""
    try:
        main([])
    except SystemExit as e:
        assert e.code == 1

    captured = capsys.readouterr()
    assert "usage:" in captured.out


def test_hello_command(capsys):
    """Test the hello command with default name."""
    main(['hello'])

    captured = capsys.readouterr()
    assert "Hello from snowleopard, World!" in captured.out


def test_hello_command_with_name(capsys):
    """Test the hello command with custom name."""
    main(['hello', '--name', 'Alice'])
    captured = capsys.readouterr()
    assert "Hello from snowleopard, Alice!" in captured.out
