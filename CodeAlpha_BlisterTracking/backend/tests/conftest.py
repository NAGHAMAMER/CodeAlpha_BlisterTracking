import pytest


def pytest_addoption(parser):
    parser.addoption('--run-model', action='store_true', help='Run the supplied YOLO weights in smoke tests.')


def pytest_collection_modifyitems(config, items):
    if not config.getoption('--run-model'):
        for item in items:
            if item.path.name == 'test_real_model.py':
                item.add_marker(pytest.mark.skip(reason='Use --run-model for model integration checks.'))
