import io
from setuptools import setup, find_packages
from pkg_resources import parse_requirements


with open('requirements.txt', encoding='utf-8') as fp:
    install_requires = [str(requirement) for requirement in parse_requirements(fp)]

setup(
    name='pydantic_validation_decorator',
    version='0.1.4',
    author_email='3055204202@qq.com',
    homepage='https://github.com/insistence/pydantic-validation-decorator',
    author='insistence <3055204202@qq.com>',
    packages=find_packages(),
    license='MIT',
    description='Some practical pydantic validation decorators that support manual invocation.',
    long_description=io.open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    classifiers=[
        'Framework :: Pydantic',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url='https://github.com/insistence/pydantic-validation-decorator',
    install_requires=install_requires,
    include_package_data=True,
)
