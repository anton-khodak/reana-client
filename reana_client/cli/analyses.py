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
"""REANA client analysis related commands."""

import logging

import click
import yaml

from ..utils import load_reana_spec, load_workflow_spec


@click.command('list')
@click.pass_context
def list_(ctx):
    """List all available analyses."""
    try:
        response = ctx.obj.client.get_all_analyses()
        for analysis in response:
            click.echo(analysis)

    except Exception as e:
        logging.info('Something went wrong when trying to connect to {0}'
                     .format(ctx.obj.client.server_url))
        logging.debug(str(e))


@click.command()
@click.option('-u', '--user', default='00000000-0000-0000-0000-000000000000',
              help='User who submits the analysis.')
@click.option('-o', '--organization', default='default',
              help='Organization which resources will be used.')
@click.pass_context
def run(ctx, user, organization):
    """Run a REANA compatible analysis using `.reana.yaml` spec."""
    try:
        reana_spec = load_reana_spec()
        reana_spec['workflow']['spec'] = load_workflow_spec(
            reana_spec['workflow']['type'],
            reana_spec['workflow']['file'],
        )
        if reana_spec['workflow']['type'] == 'cwl':
            with open(reana_spec['parameters']['input']) as f:
                reana_spec['parameters']['input'] = yaml.load(f)
        logging.info('Connecting to {0}'.format(ctx.obj.client.server_url))
        response = ctx.obj.client.run_analysis(user, organization,
                                               reana_spec)
        click.echo(response)

    except Exception as e:
        logging.error(str(e))

