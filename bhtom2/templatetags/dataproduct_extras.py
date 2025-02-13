from datetime import datetime
from urllib.parse import urlencode

import plotly.graph_objs as go
from django import template
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.shortcuts import reverse
from guardian.shortcuts import get_objects_for_user
from plotly import offline

from bhtom_base.bhtom_dataproducts.forms import DataProductUploadForm
from bhtom_base.bhtom_dataproducts.models import DataProduct, ReducedDatum, ReducedDatumUnit
from bhtom_base.bhtom_dataproducts.processors.data_serializers import SpectrumSerializer
from bhtom_base.bhtom_observations.models import ObservationRecord
from bhtom_base.bhtom_targets.models import Target

register = template.Library()


@register.inclusion_tag('bhtom_dataproducts/partials/recent_photometry.html')
def recent_photometry(target, limit=1):
    """
    Displays a table of the most recent photometric points for a target.
    """
    photometry = ReducedDatum.objects.filter(data_type='photometry', target=target).order_by('-timestamp')[:limit]
    return {'data': [{'timestamp': rd.timestamp,
                      'magnitude': rd.value} for rd in photometry
                     if rd.value_unit == ReducedDatumUnit.MAGNITUDE]}


@register.inclusion_tag('bhtom_dataproducts/partials/dataproduct_list_for_target.html', takes_context=True)
def dataproduct_list_for_target(context, target):
    """
    Given a ``Target``, returns a list of ``DataProduct`` objects associated with that ``Target``
    """
    if settings.TARGET_PERMISSIONS_ONLY:
        target_products_for_user = target.dataproduct_set.all()
    else:
        target_products_for_user = get_objects_for_user(
            context['request'].user, 'bhtom_dataproducts.view_dataproduct', klass=target.dataproduct_set.all())
    return {
        'products': target_products_for_user,
        'target': target
    }


@register.inclusion_tag('bhtom_dataproducts/partials/saved_dataproduct_list_for_observation.html')
def dataproduct_list_for_observation_saved(data_products, request):
    """
    Given a dictionary of dataproducts from an ``ObservationRecord``, returns the subset that are saved to the TOM. This
    templatetag paginates the subset of ``DataProduct``, and therefore requires the request to have a 'page_saved' key.

    This templatetag is intended to be used with the ``all_data_products()`` method from a facility, as it returns a
    dictionary with keys of ``saved`` and ``unsaved`` that have values of lists of ``DataProduct`` objects.
    """
    page = request.GET.get('page_saved')
    paginator = Paginator(data_products['saved'], 25)
    products_page = paginator.get_page(page)
    return {'products_page': products_page}


@register.inclusion_tag('bhtom_dataproducts/partials/unsaved_dataproduct_list_for_observation.html')
def dataproduct_list_for_observation_unsaved(data_products):
    """
    Given a dictionary of dataproducts from an ``ObservationRecord``, returns a list of the subset that are not saved to
    the TOM.

    This templatetag is intended to be used with the ``all_data_products()`` method from a facility, as it returns a
    dictionary with keys of ``saved`` and ``unsaved`` that have values of lists of ``DataProduct`` objects.
    """
    return {'products': data_products['unsaved']}


@register.inclusion_tag('bhtom_dataproducts/partials/dataproduct_list.html', takes_context=True)
def dataproduct_list_all(context):
    """
    Returns the full list of data products in the TOM, with the most recent first.
    """
    if settings.TARGET_PERMISSIONS_ONLY:
        products = DataProduct.objects.all().order_by('-created')
    else:
        products = get_objects_for_user(context['request'].user, 'bhtom_dataproducts.view_dataproduct')
    return {'products': products}


@register.inclusion_tag('bhtom_dataproducts/partials/upload_dataproduct.html', takes_context=True)
def upload_dataproduct(context, obj):
    user = context['user']
    initial = {}
    if isinstance(obj, Target):
        initial['target'] = obj
        initial['referrer'] = reverse('bhtom_base.bhtom_targets:detail', args=(obj.id,))
    elif isinstance(obj, ObservationRecord):
        initial['observation_record'] = obj
        initial['referrer'] = reverse('bhtom_base.bhtom_observations:detail', args=(obj.id,))
    form = DataProductUploadForm(initial=initial)
    if not settings.TARGET_PERMISSIONS_ONLY:
        if user.is_superuser:
            form.fields['groups'].queryset = Group.objects.all()
        else:
            form.fields['groups'].queryset = user.groups.all()
    return {'data_product_form': form}


@register.inclusion_tag('bhtom_dataproducts/partials/photometry_for_target.html', takes_context=True)
def photometry_for_target(context, target, width=700, height=600, background=None, label_color=None, grid=True):
    """
    Renders a photometric plot for a target.

    This templatetag requires all ``ReducedDatum`` objects with a data_type of ``photometry`` to be structured with the
    following keys in the JSON representation: magnitude, error, filter

    :param width: Width of generated plot
    :type width: int

    :param height: Height of generated plot
    :type width: int

    :param background: Color of the background of generated plot. Can be rgba or hex string.
    :type background: str

    :param label_color: Color of labels/tick labels. Can be rgba or hex string.
    :type label_color: str

    :param grid: Whether to show grid lines.
    :type grid: bool
    """

    color_map = {
        'r': 'red',
        'g': 'green',
        'i': 'black'
    }

    photometry_data = {}
    if settings.TARGET_PERMISSIONS_ONLY:
        datums = ReducedDatum.objects.filter(target=target,
                                             data_type=settings.DATA_PRODUCT_TYPES['photometry'][0])
    else:
        datums = get_objects_for_user(context['request'].user,
                                      'bhtom_dataproducts.view_reduceddatum',
                                      klass=ReducedDatum.objects.filter(
                                          target=target,
                                          data_type=settings.DATA_PRODUCT_TYPES['photometry'][0],
                                          value_unit=ReducedDatumUnit.MAGNITUDE))

    for datum in datums:
        photometry_data.setdefault(datum.filter, {})
        photometry_data[datum.filter].setdefault('time', []).append(datum.timestamp)
        photometry_data[datum.filter].setdefault('magnitude', []).append(datum.value)
        photometry_data[datum.filter].setdefault('error', []).append(datum.error)

        # TODO: handle limits
        # photometry_data[datum.filter].setdefault('limit', []).append(datum.value.get('limit'))

    plot_data = []
    for filter_name, filter_values in photometry_data.items():
        if filter_values['magnitude']:
            series = go.Scatter(
                x=filter_values['time'],
                y=filter_values['magnitude'],
                mode='markers',
                marker=dict(color=color_map.get(filter_name)),
                name=filter_name,
                error_y=dict(
                    type='data',
                    array=filter_values['error'],
                    visible=True
                )
            )
            plot_data.append(series)
        # if filter_values['limit']:
        #     series = go.Scatter(
        #         x=filter_values['time'],
        #         y=filter_values['limit'],
        #         mode='markers',
        #         opacity=0.5,
        #         marker=dict(color=color_map.get(filter_name)),
        #         marker_symbol=6,  # upside down triangle
        #         name=filter_name + ' non-detection',
        #     )
        #     plot_data.append(series)

    layout = go.Layout(
        yaxis=dict(autorange='reversed'),
        height=height,
        width=width,
        paper_bgcolor=background,
        plot_bgcolor=background

    )
    layout.legend.font.color = label_color
    fig = go.Figure(data=plot_data, layout=layout)
    fig.update_yaxes(showgrid=grid, color=label_color, showline=True, linecolor=label_color, mirror=True)
    fig.update_xaxes(showgrid=grid, color=label_color, showline=True, linecolor=label_color, mirror=True)
    return {
        'target': target,
        'plot': offline.plot(fig, output_type='div', show_link=False)
    }


@register.inclusion_tag('bhtom_dataproducts/partials/spectroscopy_for_target.html', takes_context=True)
def spectroscopy_for_target(context, target, dataproduct=None):
    """
    Renders a spectroscopic plot for a ``Target``. If a ``DataProduct`` is specified, it will only render a plot with
    that spectrum.
    """
    spectral_dataproducts = DataProduct.objects.filter(target=target,
                                                       data_product_type=settings.DATA_PRODUCT_TYPES['spectroscopy'][0])
    if dataproduct:
        spectral_dataproducts = DataProduct.objects.get(data_product=dataproduct)

    plot_data = []
    if settings.TARGET_PERMISSIONS_ONLY:
        datums = ReducedDatum.objects.filter(data_product__in=spectral_dataproducts)
    else:
        datums = get_objects_for_user(context['request'].user,
                                      'bhtom_dataproducts.view_reduceddatum',
                                      klass=ReducedDatum.objects.filter(data_product__in=spectral_dataproducts))
    for datum in datums:
        deserialized = SpectrumSerializer().deserialize(datum.value)
        plot_data.append(go.Scatter(
            x=deserialized.wavelength.value,
            y=deserialized.flux.value,
            name=datetime.strftime(datum.timestamp, '%Y%m%d-%H:%M:%s')
        ))

    layout = go.Layout(
        height=600,
        width=700,
        xaxis=dict(
            tickformat="d"
        ),
        yaxis=dict(
            tickformat=".1eg"
        )
    )
    return {
        'target': target,
        'plot': offline.plot(go.Figure(data=plot_data, layout=layout), output_type='div', show_link=False)
    }


@register.inclusion_tag('bhtom_dataproducts/partials/update_broker_data_button.html', takes_context=True)
def update_broker_data_button(context):
    return {'query_params': urlencode(context['request'].GET.dict())}
