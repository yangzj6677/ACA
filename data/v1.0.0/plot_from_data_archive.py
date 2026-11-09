"""Rebuild manuscript Figures 1 and 2 from two hash-verified data-ZIP CSVs.

No original experiment workspace, model, waveform, labels, or network is used.
"""
# MIT License
#
# Copyright (c) 2026 ACA contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import tempfile
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

INPUTS = ('results/E6/machine_contrasts.csv', 'results/E7/aggregate.csv')
SUPPORTED_ARCHIVES = {
    '2bb8d996977d76d89a302c90525346e066abe5c3294c5101abb940f546f86431': 'research_data_v1.0.0.zip',
    'b8a3e4e9299faa255752c1bf60357fa75fef6defbd5c36b552b812b98cadbe67': 'research_data_deposit_E18_20261031.zip',
}
VIEWS = ('BEATs', 'CLS', 'FM')
YEARS = ('2024', '2025')
METHODS = (('residual_ridge', 'o', 'Paired'),
           ('covariance_only', 's', 'Covariance'),
           ('shuffled_target', 'x', 'Shuffled'))


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def number(row, field):
    value = float(row[field])
    if not math.isfinite(value):
        raise ValueError(f'Non-finite {field}: {row}')
    return value


def read_tables(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive members')
        manifest = json.loads(archive.read('manifest.json'))['files']
        payload = {name: archive.read(name) for name in INPUTS}
        hashes = {name: sha_bytes(data) for name, data in payload.items()}
        for name, digest in hashes.items():
            if digest != manifest[name]['SHA256']:
                raise ValueError(f'Manifest hash mismatch: {name}')
    tables = {name: list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'), newline='')))
              for name, data in payload.items()}
    angular, interfaces = (tables[name] for name in INPUTS)
    expected = {(view, year) for view in VIEWS for year in YEARS}
    if len(angular) != 51:
        raise ValueError('Expected all 51 machine/view contrasts')
    keys = {(r['view'], r['year'], r['machine']) for r in angular}
    if len(keys) != 51 or {(r['view'], r['year']) for r in angular} != expected:
        raise ValueError('Incomplete or duplicate machine/view contrasts')
    for view, year in expected:
        count = sum(r['view'] == view and r['year'] == year for r in angular)
        if count != (9 if year == '2024' else 8):
            raise ValueError(f'Unexpected machine count: {view}/{year}')
    expected_interface = {(view, year, method) for view, year in expected
                          for method, _, _ in METHODS}
    if len(interfaces) != 18 or {(r['view'], r['year'], r['method']) for r in interfaces} != expected_interface:
        raise ValueError('Expected all 18 view/year/method interface contrasts')
    ordered_groups = [[(r['view'], r['year']) for r in interfaces if r['method'] == method]
                      for method, _, _ in METHODS]
    if any(groups != ordered_groups[0] for groups in ordered_groups[1:]):
        raise ValueError('Interface rows have inconsistent group ordering')
    numeric = {
        'figure1': [dict(view=r['view'], year=r['year'], machine=r['machine'],
                         x=number(r, 'D_angle'), H=number(r, 'D_H'),
                         oracle_TPR10=number(r, 'D_T')) for r in angular],
        'figure2': [dict(view=r['view'], year=r['year'], method=r['method'],
                         noisy_H=number(r, 'noisy_D_H_vs_joint'),
                         original_H=number(r, 'original_D_H_vs_joint')) for r in interfaces],
    }
    return angular, interfaces, hashes, numeric


def draw_figures(angular, interfaces, output):
    plt.rcdefaults()
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams.update({'font.size': 9, 'axes.titlesize': 10, 'axes.labelsize': 8,
                         'legend.fontsize': 8})
    fig, axes = plt.subplots(3, 2, figsize=(6.9, 8.0))
    for row, view in enumerate(VIEWS):
        for col, metric in enumerate(('D_H', 'D_T')):
            ax = axes[row, col]
            for year, marker in (('2024', 'o'), ('2025', 's')):
                rows = [r for r in angular if r['view'] == view and r['year'] == year]
                ax.scatter([number(r, 'D_angle') for r in rows],
                           [number(r, metric) for r in rows], marker=marker, s=28, label=year)
            ax.axvline(0, c='gray', lw=.7)
            ax.axhline(0, c='gray', lw=.7)
            ax.set_xlabel('Angular error shuffled minus paired')
            ax.set_ylabel('H paired minus shuffled' if col == 0
                          else 'Oracle TPR10 paired minus shuffled')
            ax.set_title(view + (' sensitivity' if view == 'FM' else ''))
            ax.grid(alpha=.15)
            if row == 0 and col == 0:
                ax.legend()
    fig.tight_layout()
    counts1 = [sum(len(series.get_offsets()) for series in ax.collections)
               for ax in axes.flat]
    fig.savefig(output / 'figure1.png', dpi=220)
    fig.savefig(output / 'figure1.pdf', metadata={'CreationDate': None})
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.9))
    for method, marker, label in METHODS:
        rows = [r for r in interfaces if r['method'] == method]
        labels = [r['view'] + ' ' + r['year'][2:] for r in rows]
        for ax, key in zip(axes, ('noisy_D_H_vs_joint', 'original_D_H_vs_joint')):
            ax.scatter([number(r, key) for r in rows], range(6), marker=marker,
                       label=label, s=30)
    for ax, title in zip(axes, ('Noisy H difference', 'Original H difference')):
        ax.set_yticks(range(6), labels)
        ax.axvline(0, c='gray', lw=.7)
        ax.set_title(title)
        ax.set_xlabel('Original reference minus joint map')
        ax.grid(axis='x', alpha=.2)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, .92))
    counts2 = [sum(len(series.get_offsets()) for series in ax.collections) for ax in axes]
    fig.savefig(output / 'figure2.png', dpi=220)
    fig.savefig(output / 'figure2.pdf', metadata={'CreationDate': None})
    plt.close(fig)
    if counts1 != [17] * 6 or counts2 != [18] * 2:
        raise ValueError(f'Unexpected plotted point counts: {counts1}, {counts2}')
    return counts1, counts2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, help='Verified research-data ZIP (v1.0.0 or the sealed E18 archive)')
    parser.add_argument('--output', type=Path, required=True,
                        help='New directory; existing outputs are preserved')
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f'Choose a new output directory: {args.output}')
    archive_hash = sha_file(args.archive)
    if archive_hash not in SUPPORTED_ARCHIVES:
        parser.error(f'Unsupported archive SHA-256 {archive_hash}. Expected one of {SUPPORTED_ARCHIVES}.')
    angular, interfaces, hashes, numeric = read_tables(args.archive)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=args.output.parent) as scratch:
        output = Path(scratch) / 'figures'
        output.mkdir()
        counts1, counts2 = draw_figures(angular, interfaces, output)
        (output / 'numeric_points.json').write_text(json.dumps(numeric, indent=2) + '\n', encoding='utf-8')
        result = {
            'state': 'figures_rebuilt_from_verified_archive_tables',
            'archive_name': args.archive.name, 'archive_SHA256': archive_hash,
            'source_SHA256': hashes, 'script_SHA256': sha_file(Path(__file__)),
            'python': platform.python_version(), 'matplotlib': matplotlib.__version__,
            'figure1_machine_view_rows': len(angular), 'figure1_plotted_points': sum(counts1),
            'figure2_group_method_rows': len(interfaces), 'figure2_plotted_points': sum(counts2),
            'points_per_panel': {'figure1': counts1, 'figure2': counts2},
            'output_SHA256': {name: sha_file(output / name) for name in
                              ('figure1.png', 'figure1.pdf', 'figure2.png', 'figure2.pdf', 'numeric_points.json')},
            'scope': 'Plot regeneration from retained numerical contrasts; no raw-audio, model, or metric recomputation.',
        }
        (output / 'validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        output.rename(args.output)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
