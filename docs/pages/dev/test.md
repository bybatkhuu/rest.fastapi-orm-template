# 🧪 Test

To run tests, run the following command:

```sh
# Install python test dependencies:
pip install -r ./requirements/requirements.test.txt

# Run tests:
./scripts/test.sh -l -v -c
# Or:
python -m pytest -sv -o log_cli=true
```

## Pytest

```sh
# Install pytest:
pip install -U pytest pytest-cov pytest-xdist pytest-benchmark

# Run tests:
python -m pytest

# Pytest help:
python -m pytest --help
```

## References

- [Pytest Documentation](https://docs.pytest.org/en/latest)
- [Pytest Getting Started](https://docs.pytest.org/en/latest/getting-started.html)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/reference/fixtures.html)
- Blogs:
    - <https://docs.pytest.org/en/latest/goodpractices.html>
    - <https://emimartin.me/pytest_best_practices>
    - <https://esaezgil.com/post/unittesting_pitfalls>
    - <https://pytest-with-eric.com/mocking/pytest-common-mocking-problems>
