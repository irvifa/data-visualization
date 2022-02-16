from setuptools import find_packages, setup

setup(
    name="data-visualization",
    use_scm_version={"version_scheme": "post-release", "local_scheme": "dirty-tag"},
    setup_requires=["setuptools_scm"],
    include_package_data=True,
    install_requires=[
        "ipython >= 4",
        "notebook >= 4.3.1",
        "jupyter",
        "pandas",
        "numpy",
        "pyxlsb",
        "matplotlib",
    ],
    zip_safe=False,
)
