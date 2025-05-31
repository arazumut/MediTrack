"use strict";

var KTLayoutDocumentation = function() {
    var menuWrapper;
    var keeniconsListing;
    var selectedIconName;
    var selectedIconCode;

    var initInstance = function(element) {
        var elements = element;

        if ( typeof elements === 'undefined' ) {
            elements = document.querySelectorAll('.highlight');
        }

        if ( elements && elements.length > 0 ) {
            for ( var i = 0; i < elements.length; ++i ) {
                var highlight = elements[i];
                var copy = highlight.querySelector('.highlight-copy');

                if ( copy ) {
                    var clipboard = new ClipboardJS(copy, {
                        target: function(trigger) {
                            var highlight = trigger.closest('.highlight');
                            var el = highlight.querySelector('.tab-pane.active');

                            if ( el == null ) {
                                el = highlight.querySelector('.highlight-code');
                            }

                            return el;
                        }
                    });

                    clipboard.on('success', function(e) {
                        var caption = e.trigger.innerHTML;

                        e.trigger.innerHTML = 'copied';
                        e.clearSelection();

                        setTimeout(function() {
                            e.trigger.innerHTML = caption;
                        }, 2000);
                    });
                }
            }
        }
    }

    var handleMenuScroll = function() {
        var menuActiveItem = menuWrapper.querySelector(".menu-link.active");

        if ( !menuActiveItem ) {
            return;
        } 

        if ( KTUtil.isVisibleInContainer(menuActiveItem, menuWrapper) === true) {
            return;
        }

        menuWrapper.scroll({
            top: KTUtil.getRelativeTopPosition(menuActiveItem, menuWrapper),
            behavior: 'smooth'
        });
    }

    var keeniconsStyleToggle = function() {
        var toggleButtons = [].slice.call(document.querySelectorAll('[data-kt-keenicons-style-toggle="true"]'));

        function escapeHtml(text) {
            if (text == null) return '';

            return String(text).
                replace(/&/g, '&amp;').
                replace(/</g, '&lt;').
                replace(/>/g, '&gt;').
                replace(/"/g, '&quot;').
                replace(/'/g, '&#039;');
        }

        KTUtil.on(document.body, '[data-kt-keenicons-style-toggle="true"]:checked', 'click', function (e) {
            var style = this.value;

            keeniconsListing.classList.remove('keenicons-solid');
            keeniconsListing.classList.remove('keenicons-duotone');
            keeniconsListing.classList.remove('keenicons-outline');
            keeniconsListing.classList.add('keenicons-' + style);
        });    

        KTUtil.on(document.body, '[data-kt-icon-use="true"]', 'click', function (e) {
            var style = document.querySelector('[data-kt-keenicons-style-toggle="true"]:checked').value;

            var previewEl = this.closest('[data-kt-icon-preview="true"]');
            var iconNameEl = previewEl.querySelector('[data-kt-icon-name="true"]');

            selectedIconName = iconNameEl.innerHTML;
            if (style === 'duotone') {
                const paths = parseInt(this.getAttribute('data-kt-icon-paths'));
                selectedIconCode = escapeHtml('<i class="ki-duotone ki-' + selectedIconName + '">');
                for (let i = 1; i <= paths; i++) {
                    selectedIconCode += escapeHtml('\n <span class="path' + i + '"></span>');
                }
                selectedIconCode += escapeHtml('\n</i>');
            } else {
                selectedIconCode = escapeHtml('<i class="ki-' + style + ' ki-' + selectedIconName + '"></i>');
            }
            
            const myModalEl = new bootstrap.Modal('#kt_keenicons_use');
            myModalEl.show();
        });

        const myModalEl = document.getElementById('kt_keenicons_use');
        myModalEl.addEventListener('show.bs.modal', event => {
            document.querySelector('#kt_keenicons_use_title').innerHTML = selectedIconName;
            document.querySelector('#kt_keenicons_use_code').innerHTML = selectedIconCode;
        });

        // Copy
    }

    var keeniconsHandleCodeCopy = function() {
        // Select elements
        const target = document.getElementById('kt_keenicons_use_code');
        const button = document.getElementById('kt_keenicons_use_code_copy');

        // Init clipboard -- for more info, please read the offical documentation: https://clipboardjs.com/
        var clipboard = new ClipboardJS(button, {
            target: target,
            text: function(target) {
                return target.innerText;
            }
        });

        // Success action handler
        clipboard.on('success', function(e) {
            button.classList.add('active');
            button.querySelector('.ki-copy').classList.add('d-none');
            button.querySelector('.ki-check').classList.remove('d-none');

            setTimeout(function(){
                button.classList.remove('active');
                button.querySelector('.ki-copy').classList.remove('d-none');
                button.querySelector('.ki-check').classList.add('d-none');
            }, 3000);
        });
    }

    return {
        init: function(element) {
            menuWrapper = document.querySelector('#kt_docs_aside_menu_wrapper');
            keeniconsListing = document.querySelector('#kt_docs_keenicons_listing');

            initInstance(element);

            if (menuWrapper) {
                handleMenuScroll();
            }            

            if (keeniconsListing) {
                keeniconsStyleToggle();
                keeniconsHandleCodeCopy();
            }
        }
    };
}();

// On document ready
KTUtil.onDOMContentLoaded(function() {
    KTLayoutDocumentation.init();
});