# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2017 CERN.
#
# REANA is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# REANA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# REANA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization or
# submit itself to any jurisdiction.
"""REANA client workflow related commands."""

import logging
import os
import random
import uuid
from enum import Enum

import click
import tablib

from ..config import (default_organisation, default_user,
                      reana_yaml_default_file_path)
from ..utils import load_reana_spec, load_workflow_spec
from .namesgenerator import get_random_name


class _WorkflowStatus(Enum):
    created = 0
    running = 1
    finished = 2
    failed = 3


@click.group(
    help='All interaction related to workflows on REANA cloud.')
@click.pass_context
def workflow(ctx):
    """Top level wrapper for workflow related interaction."""
    logging.debug('workflow')


@click.command(
    'list',
    help='List all available workflows.')
@click.option(
    '--filter',
    multiple=True,
    help='Filter output according to column titles (case-sensitive).')
@click.option(
    '-of',
    '--output-format',
    type=click.Choice(['json', 'yaml']),
    help='Set output format.')
@click.pass_context
def workflow_list(ctx, filter, output_format):
    """List all available workflows."""
    logging.debug('workflow.list')

    data = tablib.Dataset()
    data.headers = ['Name', 'UUID', 'Status']

    for i in range(1, 10):
        data.append([get_random_name(),
                     uuid.uuid1(),
                     random.choice(list(_WorkflowStatus)).name])

    if filter:
        data = data.subset(rows=None, cols=list(filter))

    if output_format:
        click.echo(data.export(output_format))
    else:
        click.echo(data)

    # try:
    #     response = ctx.obj.client.get_all_analyses()
    #     for analysis in response:
    #         click.echo(analysis)
    #
    # except Exception as e:
    #     logging.info('Something went wrong when trying to connect to {0}'
    #                  .format(ctx.obj.client.server_url))
    #     logging.debug(str(e))


@click.command(
    'create',
    help='Create a REANA compatible analysis workflow from REANA '
         'specifications file.')
@click.option(
    '-f',
    '--file',
    type=click.Path(exists=True, resolve_path=True),
    default=reana_yaml_default_file_path,
    help='REANA specifications file describing the workflow and '
         'context which REANA should execute.')
@click.option(
    '-u',
    '--user',
    default=default_user,
    help='User who creates the analysis.')
@click.option(
    '-o',
    '--organization',
    default=default_organisation,
    help='Organization whose resources will be used.')
@click.option(
    '--skip-validation',
    is_flag=True,
    help="If set, specifications file is not validated before "
         "submitting it's contents to REANA Server.")
@click.pass_context
def workflow_create(ctx, file, user, organization, skip_validation):
    """Create a REANA compatible analysis workflow from REANA spec file."""
    logging.debug('workflow.create')
    logging.debug('file: {}'.format(file))
    logging.debug('user: {}'.format(user))
    logging.debug('organization: {}'.format(organization))
    logging.debug('skip_validation: {}'.format(skip_validation))

    click.echo('Workflow `{}` has been created.'.format(get_random_name()))

    # try:
    #     reana_spec = load_reana_spec(click.format_filename(file),
    #                                  skip_validation)
    #
    #     reana_spec['workflow']['spec'] = load_workflow_spec(
    #         reana_spec['workflow']['type'],
    #         reana_spec['workflow']['file'],
    #     )
    #
    #     logging.info('Connecting to {0}'.format(ctx.obj.client.server_url))
    #     response = ctx.obj.client.run_analysis(user, organization,
    #                                            reana_spec)
    #     click.echo(response)
    #
    # except Exception as e:
    #     logging.debug(str(e))


@click.command(
    'start',
    help='Start previously created analysis workflow.')
@click.option(
    '-u',
    '--user',
    default=default_user,
    help='User who has created the workflow.')
@click.option(
    '-o',
    '--organization',
    default=default_organisation,
    help='Organization whose resources will be used.')
@click.option(
    '--workflow',
    help='Name of the workflow to be started. '
         'Overrides value of $REANA_WORKON.')
@click.pass_context
def workflow_start(ctx, user, organization, workflow):
    """Start previously created analysis workflow."""
    logging.debug('workflow.start')
    logging.debug('user: {}'.format(user))
    logging.debug('organization: {}'.format(organization))
    logging.debug('workflow: {}'.format(workflow))

    workflow_name = workflow or os.environ.get('$REANA_WORKON', None)

    if workflow_name:
        logging.info('Workflow "{}" selected'.format(workflow_name))
        click.echo('Workflow `{}` has been started.'.format(workflow_name))
    else:
        click.echo(
            click.style('Workflow name must be provided either with '
                        '`--workflow` option or with `$REANA_WORKON` '
                        'environment variable',
                        fg='red'),
            err=True)

    # try:
    #     logging.info('Connecting to {0}'.format(ctx.obj.client.server_url))
    #     response = ctx.obj.client.start_analysis(user,
    #                                              organization,
    #                                              workflow)
    #     click.echo(response)
    #
    # except Exception as e:
    #     logging.debug(str(e))


workflow.add_command(workflow_list)
workflow.add_command(workflow_create)
workflow.add_command(workflow_start)