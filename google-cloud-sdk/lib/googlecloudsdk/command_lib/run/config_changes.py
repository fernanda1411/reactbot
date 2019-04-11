# -*- coding: utf-8 -*- #
# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Class for representing various changes to a Configuration."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

from googlecloudsdk.command_lib.run import exceptions
from googlecloudsdk.command_lib.util.args import repeated

import six


class ConfigChanger(six.with_metaclass(abc.ABCMeta, object)):
  """An abstract class representing configuration changes."""

  @abc.abstractmethod
  def AdjustConfiguration(self, config, metadata):
    """Adjust the given Service configuration.

    Args:
      config: Configuration, The service's Configuration object to adjust.
      metadata: ObjectMeta, the config's metadata message object.
    """
    pass


class EnvVarChanges(ConfigChanger):
  """Represents the user-intent to modify environment variables."""

  def __init__(self, env_vars_to_update=None,
               env_vars_to_remove=None, clear_others=False):
    """Initialize a new EnvVarChanges object.

    Args:
      env_vars_to_update: {str, str}, Update env var names and values.
      env_vars_to_remove: [str], List of env vars to remove.
      clear_others: bool, If true, clear all non-updated env vars.
    """
    self._clear_others = clear_others
    self._to_update = env_vars_to_update
    self._to_remove = env_vars_to_remove

  def AdjustConfiguration(self, config, metadata):
    """Mutates the given config's env vars to match the desired changes."""
    del metadata  # Unused, but requred by ConfigChanger's signature.

    if self._clear_others:
      config.env_vars.clear()
    elif self._to_remove:
      for env_var in self._to_remove:
        if env_var in config.env_vars: del config.env_vars[env_var]

    if self._to_update: config.env_vars.update(self._to_update)


class ResourceChanges(ConfigChanger):
  """Represents the user-intent to update resource limits."""

  def __init__(self, memory):
    self._memory = memory

  def AdjustConfiguration(self, config, metadata):
    """Mutates the given config's resource limits to match what's desired."""
    del metadata  # Unused, but requred by ConfigChanger's signature.
    config.resource_limits['memory'] = self._memory


_CLOUDSQL_ANNOTATION = 'run.googleapis.com/cloudsql-instances'


class CloudSQLChanges(ConfigChanger):
  """Represents the intent to update the cloudsql instances."""

  def __init__(self, project, region, args):
    """Initializes the intent to update the cloudsql instances.

    Args:
      project: Project to use as the default project for CloudSQL instances.
      region: Region to use as the default region for CloudSQL instances
      args: Args to the command.
    """
    self._project = project
    self._region = region
    self._args = args

  # Here we are a proxy through to the actual args to set some extra augmented
  # information on each one, so each cloudsql instance gets the region and
  # project.
  @property
  def add_cloudsql_instances(self):
    return self._AugmentArgs('add_cloudsql_instances')

  @property
  def remove_cloudsql_instances(self):
    return self._AugmentArgs('remove_cloudsql_instances')

  @property
  def set_cloudsql_instances(self):
    return self._AugmentArgs('set_cloudsql_instances')

  @property
  def clear_cloudsql_instances(self):
    return getattr(self._args, 'clear_cloudsql_instances', None)

  def _AugmentArgs(self, arg_name):
    val = getattr(self._args, arg_name, None)
    if val is None:
      return None
    return [self._Augment(i) for i in val]

  def AdjustConfiguration(self, config, metadata):
    def GetCurrentInstances():
      annotation_val = config.revision_annotations.get(_CLOUDSQL_ANNOTATION)
      if annotation_val:
        return annotation_val.split(',')
      return []

    instances = repeated.ParsePrimitiveArgs(
        self, 'cloudsql-instances', GetCurrentInstances)
    config.revision_annotations[_CLOUDSQL_ANNOTATION] = ','.join(instances)

  def _Augment(self, instance_str):
    instance = instance_str.split(':')
    if len(instance) == 3:
      ret = tuple(instance)
    elif len(instance) == 1:
      ret = self._project, self._region, instance[0]
    else:
      raise exceptions.CloudSQLError(
          'Malformed CloudSQL instance string: {}'.format(
              instance_str))
    return ':'.join(ret)


class ConcurrencyChanges(ConfigChanger):
  """Represents the user-intent to update concurrency preference."""

  def __init__(self, concurrency):
    self._concurrency = None if concurrency == 'default' else concurrency

  def AdjustConfiguration(self, config, metadata):
    """Mutates the given config's resource limits to match what's desired."""
    del metadata  # Unused, but requred by ConfigChanger's signature.
    if self._concurrency is None:
      config.deprecated_string_concurrency = None
      config.concurrency = None
    elif isinstance(self._concurrency, int):
      config.concurrency = self._concurrency
      config.deprecated_string_concurrency = None
    else:
      config.deprecated_string_concurrency = self._concurrency
      config.concurrency = None


class TimeoutChanges(ConfigChanger):
  """Represents the user-intent to update request duration."""

  def __init__(self, timeout):
    self._timeout = timeout

  def AdjustConfiguration(self, config, metadata):
    """Mutates the given config's timeout to match what's desired."""
    del metadata  # Unused, but required by ConfigChanger's signature.
    config.timeout = self._timeout
