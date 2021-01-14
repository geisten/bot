import setuptools

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
        name='blueprint',
        version='1.0',
        description='Python Blueprint Package',
        author='Germar Schlegel',
        author_email='g.schlegel@geisten.com',
        url='geisten.com',
        packages=['blueprint'],
        install_requires=install_requires,
        setup_requires=['pytest-runner'],
        tests_require = ['pytest'],
        extra_require={
            'interactive': ['matplotlib>=2.2.0', 'jupyter']
            },
        entry_points={
            'console_scripts': ['blueprint=blueprint/blueprint:main']
            }
        )
