from setuptools import setup, find_packages

setup(
    name='ytap',
    version='3.1.2',
    packages=find_packages(),
    install_requires=[
        'requests',
        'yt-dlp',
        'platformdirs',
    ],
    entry_points={
        'console_scripts': [
            'ytap=ytap.main:main',
        ],
    },
    exclude_package_data={'ytap': ['API_KEY']},
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)
