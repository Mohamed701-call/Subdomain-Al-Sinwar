from setuptools import setup, find_packages

setup(
    name="subdomain-al-sinwar",
    version="1.0.0",
    description="Passive Subdomain Enumeration Framework",
    author="Your Name",
    packages=find_packages(),
    py_modules=["main", "cli", "config"],
    install_requires=[
        "httpx",
        "rich",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "subdomain-al-sinwar=main:start_cli",
        ],
    },
    python_requires=">=3.8",
)