from setuptools import setup, find_packages

setup(
    name="subdomain-al-sinwar",
    version="3.0.0",
    description="Passive + active subdomain enumeration tool",
    packages=find_packages(),
    py_modules=["cli", "main", "config"],
    install_requires=["requests>=2.31.0", "mmh3>=4.0.0"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "subdomain-al-sinwar=main:run",
        ],
    },
)