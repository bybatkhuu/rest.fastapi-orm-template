# -*- coding: utf-8 -*-

import os
import errno
import shutil
import hashlib
from typing import List, Union

import aioshutil
import aiofiles.os
from pydantic import validate_arguments

from beans_logging import logger

from src.core.constants import WarnEnum


## Async:
@validate_arguments
async def async_create_dir(create_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Asynchronous create directory if `create_dir` doesn't exist.

    Args:
        create_dir (str, required): Create directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    if not await aiofiles.os.path.isdir(create_dir):
        try:
            _message = f"Creaing '{create_dir}' directory..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            await aiofiles.os.makedirs(create_dir)
        except OSError as err:
            if (err.errno == errno.EEXIST) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{create_dir}' directory already exists!")
            else:
                logger.error(f"Failed to create '{create_dir}' directory!")
                raise

        _message = f"Successfully created '{create_dir}' directory."
        if warn_mode == WarnEnum.ALWAYS:
            logger.success(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.EEXIST, f"'{create_dir}' directory already exists!")


@validate_arguments
async def async_remove_dir(remove_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Asynchronous remove directory if `remove_dir` exists.

    Args:
        remove_dir (str, required): Remove directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    if await aiofiles.os.path.isdir(remove_dir):
        try:
            _message = f"Removing '{remove_dir}' directory..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            await aioshutil.rmtree(remove_dir)
        except OSError as err:
            if (err.errno == errno.ENOENT) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{remove_dir}' directory doesn't exist!")
            else:
                logger.error(f"Failed to remove '{remove_dir}' directory!")
                raise

        _message = f"Successfully removed '{remove_dir}' directory."
        if warn_mode == WarnEnum.ALWAYS:
            logger.success(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.ENOENT, f"'{create_dir}' directory doesn't exist!")


@validate_arguments
async def async_remove_dirs(
    remove_dirs: List[str], warn_mode: WarnEnum = WarnEnum.DEBUG
):
    """Asynchronous remove directories if `remove_dirs` exists.

    Args:
        remove_dirs (List[str], required): Remove directories paths as list.
        warn_mode   (str      , optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    for _remove_dir in remove_dirs:
        await async_remove_dir(remove_dir=_remove_dir, warn_mode=warn_mode)


@validate_arguments
async def async_remove_file(file_path: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Asynchronous remove file if `file_path` exists.

    Args:
        file_path (str, required): Remove file path.
        warn_mode (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    if await aiofiles.os.path.isfile(file_path):
        try:
            _message = f"Removing '{file_path}' file..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            await aiofiles.os.remove(file_path)
        except OSError as err:
            if (err.errno == errno.ENOENT) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{file_path}' file doesn't exist!")
            else:
                logger.error(f"Failed to remove '{file_path}' file!")
                raise

        _message = f"Successfully removed '{file_path}' file."
        if warn_mode == WarnEnum.ALWAYS:
            logger.success(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.ENOENT, f"'{create_dir}' file doesn't exist!")


@validate_arguments
async def async_remove_files(
    file_paths: List[str], warn_mode: WarnEnum = WarnEnum.DEBUG
):
    """Asynchronous remove files if `file_paths` exists.

    Args:
        file_paths (List[str], required): Remove file paths as list.
        warn_mode  (str      , optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    for _file_path in file_paths:
        await async_remove_file(file_path=_file_path, warn_mode=warn_mode)


@validate_arguments
async def async_get_file_checksum(
    file_path: str, hash_type: str = "sha256", chunk_size: int = 4096
) -> str:
    """Asynchronous get file checksum.

    Args:
        file_path (str, required): Target file path.
        hash_type (str, optional): Hash type, for example: 'sha256', 'md5'. Defaults to 'sha256'.
        chunk_size (int, optional): Chunk size. Defaults to 4096.

    Returns:
        str: File checksum.
    """

    _file_hash: Union[hashlib.sha256, hashlib.md5]
    if hash_type == "sha256":
        _file_hash = hashlib.sha256()
    elif hash_type == "md5":
        _file_hash = hashlib.md5()
    else:
        raise ValueError(f"Unsupported hash type: {hash_type}")

    async with aiofiles.open(file_path, "rb") as _file:
        while True:
            _file_chunk = await _file.read(chunk_size)
            if not _file_chunk:
                break
            _file_hash.update(_file_chunk)

    _file_checksum = _file_hash.hexdigest()
    return _file_checksum


## Sync:
@validate_arguments
def create_dir(create_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Create directory if `create_dir` doesn't exist.

    Args:
        create_dir (str, required): Create directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    if not os.path.isdir(create_dir):
        try:
            _message = f"Creaing '{create_dir}' directory..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            os.makedirs(create_dir)
        except OSError as err:
            if (err.errno == errno.EEXIST) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{create_dir}' directory already exists!")
            else:
                logger.error(f"Failed to create '{create_dir}' directory!")
                raise

        _message = f"Successfully created '{create_dir}' directory."
        if warn_mode == WarnEnum.ALWAYS:
            logger.success(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.EEXIST, f"'{create_dir}' directory already exists!")


@validate_arguments
def remove_dir(remove_dir: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Remove directory if `remove_dir` exists.

    Args:
        remove_dir (str, required): Remove directory path.
        warn_mode  (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    if os.path.isdir(remove_dir):
        try:
            _message = f"Removing '{remove_dir}' directory..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            shutil.rmtree(remove_dir)
        except OSError as err:
            if (err.errno == errno.ENOENT) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{remove_dir}' directory doesn't exist!")
            else:
                logger.error(f"Failed to remove '{remove_dir}' directory!")
                raise

        _message = f"Successfully removed '{remove_dir}' directory."
        if warn_mode == WarnEnum.ALWAYS:
            logger.success(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.ENOENT, f"'{create_dir}' directory doesn't exist!")


@validate_arguments
def remove_dirs(remove_dirs: List[str], warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Remove directories if `remove_dirs` exist.

    Args:
        remove_dirs (List[str], required): Remove directory paths as list.
        warn_mode   (str      , optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    for _remove_dir in remove_dirs:
        remove_dir(remove_dir=_remove_dir, warn_mode=warn_mode)


@validate_arguments
def remove_file(file_path: str, warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Remove file if `file_path` exists.

    Args:
        file_path (str, required): Remove file path.
        warn_mode (str, optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    if os.path.isfile(file_path):
        try:
            _message = f"Removing '{file_path}' file..."
            if warn_mode == WarnEnum.ALWAYS:
                logger.info(_message)
            elif warn_mode == WarnEnum.DEBUG:
                logger.debug(_message)

            os.remove(file_path)
        except OSError as err:
            if (err.errno == errno.ENOENT) and (warn_mode == WarnEnum.DEBUG):
                logger.debug(f"'{file_path}' file doesn't exist!")
            else:
                logger.error(f"Failed to remove '{file_path}' file!")
                raise

        _message = f"Successfully removed '{file_path}' file."
        if warn_mode == WarnEnum.ALWAYS:
            logger.success(_message)
        elif warn_mode == WarnEnum.DEBUG:
            logger.debug(_message)

    elif warn_mode == WarnEnum.ERROR:
        raise OSError(errno.ENOENT, f"'{create_dir}' file doesn't exist!")


@validate_arguments
def remove_files(file_paths: List[str], warn_mode: WarnEnum = WarnEnum.DEBUG):
    """Remove files if `file_paths` exist.

    Args:
        file_paths (List[str], required): Remove file paths as list.
        warn_mode  (str      , optional): Warning message mode, for example: 'ERROR', 'ALWAYS', 'DEBUG', 'IGNORE'. Defaults to 'DEBUG'.
    """

    for _file_path in file_paths:
        remove_file(file_path=_file_path, warn_mode=warn_mode)


@validate_arguments
def get_file_checksum(
    file_path: str, hash_type: str = "sha256", chunk_size: int = 4096
) -> str:
    """Get file checksum.

    Args:
        file_path  (str, required): Target file path.
        hash_type  (str, optional): Hash type, for example: 'sha256', 'md5'. Defaults to 'sha256'.
        chunk_size (int, optional): Chunk size. Defaults to 4096.

    Returns:
        str: File checksum.
    """

    _file_hash: Union[hashlib.sha256, hashlib.md5]
    if hash_type == "sha256":
        _file_hash = hashlib.sha256()
    elif hash_type == "md5":
        _file_hash = hashlib.md5()
    else:
        raise ValueError(f"Unsupported hash type: {hash_type}")

    with open(file_path, "rb") as _file:
        while True:
            _file_chunk = _file.read(chunk_size)
            if not _file_chunk:
                break
            _file_hash.update(_file_chunk)

    _file_checksum = _file_hash.hexdigest()
    return _file_checksum


__all__ = [
    "async_create_dir",
    "async_remove_dir",
    "async_remove_dirs",
    "async_remove_file",
    "async_remove_files",
    "async_get_file_checksum",
    "create_dir",
    "remove_dir",
    "remove_dirs",
    "remove_file",
    "remove_files",
    "get_file_checksum",
]
