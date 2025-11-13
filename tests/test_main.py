from snowleopard import main


def test_main():
    """Test that main function runs without error."""
    main()


def test_main_output(capsys):
    """Test that main function prints expected output."""
    main()
    captured = capsys.readouterr()
    assert "Hello from snowleopard!" in captured.out
