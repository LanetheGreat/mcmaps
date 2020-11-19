/**
  * Copyright 2020 Lane Shaw
  *
  * Licensed under the Apache License, Version 2.0 (the "License");
  * you may not use this file except in compliance with the License.
  * You may obtain a copy of the License at
  *
  * http://www.apache.org/licenses/LICENSE-2.0
  *
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
**/

import 'jquery.ajaxq'
import 'jquery-ui/ui/widgets/draggable';
import 'jquery-ui/ui/position';
import 'jquery-ui/themes/base/draggable.css';
import _ from 'lodash';

function inViewport(rect, vp) {
    return (
        rect.top <= vp.bottom && rect.bottom >= vp.top &&
        rect.left <= vp.right && rect.right >= vp.left
    );
}

$(document).ready(function() {
    const scale = 2, scaleX16 = scale * 16;

    const seedInput  = $('#seed');
    const seedValue  = $('#numSeed');
    const worldValue = $('#wtype');
    const verValue   = $('#version');
    const container  = $('.chunk-container');
    const msgBox     = $('#msgBox');
    const chunks = {};
    const queryQueue = $.ajaxq.Queue(10);

    let seed, wtype, version;
    let vpCenter = { x: 0, z: 0 };
    let viewport = { top: 0, left: 0, bottom: 0, right: 0 };

    // Check if we need to do a map update if our input values have changed.
    function checkUpdate() {
        let update = false;

        if (seed != seedValue.val()) {
            update = true;
            seed = seedValue.val();
        }

        if (wtype != worldValue.val()) {
            update = true;
            wtype = worldValue.val();
        }

        if (version != verValue.val()) {
            update = true;
            version = verValue.val();
        }

        if (update && seed !== null && seed !== undefined && wtype && version) {
            // Purge any cached chunks and stop active requests.
            for (const z in chunks) {
                const chunkRow = chunks[z];
                delete chunks[z];

                for (const x in chunkRow) {
                    const chunk = chunkRow[x];
                    delete chunkRow[x];

                    if (chunk.request)
                        chunk.request.abort();
                    if (chunk.element)
                        chunk.element.remove();
                }
            }

            updateMap();
        }
    }

    container.draggable({
        grid: [scaleX16, scaleX16],
    });

    container.on('dragstop', () => {
        container.position({
            my: 'left top',
            at: 'left top',
            of: container.parent(),
        });
    });

    // Throttle our seed number conversion, only 1.5 seconds after input changes.
    let updateSeed = _.debounce(() => {
        if (seedInput.val() !== '')
            $.get('/api/seed?seed=' + seedInput.val())
            .done( (data) => {
                seedValue.val(data);
                seedValue.trigger('change');
            });
    }, 2000);

    function processChunk(response) {
        delete this.request;
        this.element.empty();
        if (response.image)
            $('<img/>')
            .attr('src', response.image)
            .appendTo(this.element);
    }

    function stopUpdate() {
        for (let z in chunks) {
            const chunkRow = chunks[z];
            for (let x in chunkRow) {
                const chunk = chunkRow[x];
                if (chunk.request && chunk.request.abort)
                    chunk.request.abort();
            }
        }
    }
    $('button.abort').click(stopUpdate);

    // On numeric seed update, process a new map.
    function updateMap() {
        console.log(`New map generating with seed: ${seed}, version: ${version}, type: ${wtype}`);
        let vpWidth = container.width() / 2 / scale,
            vpHeight = container.height() / 2 / scale;
        let cX = vpCenter.x,
            cZ = vpCenter.z;

        msgBox.fadeOut('slow');

        // Calculate the new viewport given the width, height, and center point.
        viewport = {
            top:    cZ - vpHeight,
            left:   cX - vpWidth,
            bottom: cZ + vpHeight,
            right:  cX + vpWidth,
        };

        const zMin = Math.floor(viewport.top   / 16),
              zMax = Math.ceil(viewport.bottom / 16),
              xMin = Math.floor(viewport.left  / 16),
              xMax = Math.ceil(viewport.right  / 16);

        // Add new chunk rows to the chunk directory.
        for (let z=zMin; z<zMax; z++) {
            let chunkRow = chunks[z];
            if (!chunkRow)
                chunkRow = chunks[z] = {};

            for (let x=xMin; x<xMax; x++) {
                if (chunkRow[x])
                    continue;

                const chunk = chunkRow[x] = {
                    element: $('<div>X</div>').addClass('chunk').appendTo(container),
                    rect: {
                        top:    z * scaleX16,
                        left:   x * scaleX16,
                        bottom: z * scaleX16 + scaleX16,
                        right:  x * scaleX16 + scaleX16,
                    },
                };
                const element = chunk.element[0];
                element.style.top = chunk.rect.top + vpHeight * scale;
                element.style.left = chunk.rect.left + vpWidth * scale;

                // Get the chunk's image URL and data.
                chunk.request = queryQueue.ajax({
                    context: chunk,
                    url: '/api/biomes?' + [
                        'seed=' + seed,
                        'wtype=' + wtype,
                        'version=' + version,
                        'x=' + x,
                        'z=' + z,
                    ].join('&'),
                    dataType: 'json',
                }).done(processChunk);
            }
        }
    }

    // Register our input update handlers.
    seedValue.on('change', checkUpdate);
    worldValue.on('change', checkUpdate);
    verValue.on('change', checkUpdate);

    seedInput.on('input', (e) => {
        e.stopImmediatePropagation();
        updateSeed();
    });
});
