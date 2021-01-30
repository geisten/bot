import setuptools

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name='bot',
    version='1.0',
    description='Python Blueprint Package',
    author='Germar Schlegel',
    author_email='g.schlegel@geisten.com',
    url='geisten.com',
    packages=['bot'],
    install_requires=install_requires,
    setup_requires=['pytest-runner', 'flake8', 'mypy', 'bandit'],
    tests_require=['pytest'],
    extras_require={
        'interactive': ['matplotlib>=2.2.0', 'jupyter']
    },
    entry_points={
        'console_scripts': ['bot=app:main']
    }
)
