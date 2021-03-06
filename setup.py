from setuptools import setup

setup(
    use_scm_version={
        'version_scheme': 'guess-next-dev',
        'local_scheme': 'dirty-tag',
    },
    setup_requires=[
        'setuptools_scm >= 1.7.0',
        'setuptools >= 36.2.7'
    ]
)
