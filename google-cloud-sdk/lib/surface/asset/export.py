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
"""Command to export assets to Google Cloud Storage."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.asset import client_util
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.asset import flags
from googlecloudsdk.command_lib.asset import utils as asset_utils
from googlecloudsdk.core import log


OPERATION_DESCRIBE_COMMAND = 'gcloud asset operations describe'


# pylint: disable=line-too-long
class Export(base.Command):
  """Export the cloud assets to Google Cloud Storage."""

  detailed_help = {
      'DESCRIPTION':
          """\
      Export the cloud assets to Google Cloud Storage. Use gcloud asset operations
      describe to get the latest status of the operation. Note that to use this
      command, you must be authenticated with a service account.
      See https://cloud.google.com/resource-manager/docs/cloud-asset-inventory/gcloud-asset
      for more details.
      """,
      'EXAMPLES':
          """\
      To export a snapshot of assets of type 'compute.googleapis.com/Disk' in
      project 'test-project' at '2019-03-05T00:00:00Z' to
      'gs://bucket-name/object-name' and only export the asset metadata, run:

        $ {command} --project='test-project' --asset-types='compute.googleapis.com/Disk' --snapshot-time='2019-03-05T00:00:00Z' --output-path='gs://bucket-name/object-name' --content-type='resource'
      """
  }
  # pylint: enable=line-too-long

  @staticmethod
  def Args(parser):
    flags.AddParentArgs(parser)
    flags.AddSnapshotTimeArgs(parser)
    flags.AddAssetTypesArgs(parser)
    flags.AddContentTypeArgs(parser, required=False)
    flags.AddOutputPathArgs(parser)

  def Run(self, args):
    parent = asset_utils.GetParentName(args.organization, args.project,
                                       args.folder)
    client = client_util.AssetExportClient(parent)
    operation = client.Export(args)

    log.ExportResource(parent, is_async=True, kind='root asset')
    log.status.Print('Use [{} {}] to check the status of the operation.'.format(
        OPERATION_DESCRIBE_COMMAND, operation.name))
