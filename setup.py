from setuptools import setup


setup(
    name='cdflow',
    version='dev',
    scripts=['cdflow.py'],
    entry_points={
        'console_scripts': [
            'cdflow = cdflow:run',
        ],
    },
    install_requires=[
        'boto3',
        'docker',
        'pyyaml>=4.2b1',
        'dockerpty',
    ],
    author='Acuris',
    author_email='platform@acuris.com',
    description='Deployment tooling for continuous delivery',
    keywords='continuous delivery terraform',
    url='https://mergermarket.github.io/cdflow',
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
)
