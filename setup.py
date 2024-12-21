from setuptools import setup, find_packages

setup(
    name='ytap',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'yt-dlp'
    ],
    entry_points={
        'console_scripts': [
            'ytap=main:main',
        ],
    },
    package_data={
        '': ['config/API_KEY'],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)