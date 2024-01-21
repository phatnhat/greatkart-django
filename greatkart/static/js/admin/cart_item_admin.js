window.addEventListener("load", function() {
    (function($) {
        $(document).ready(function() {
            let currentPathname  = window.location.pathname;
            if(currentPathname.indexOf('/change/') !== -1){
                var productField = $('#id_product');
                var variationsField = $('#id_variations');
                var currentId = window.location.pathname.split('/').slice(-3, -1)[0];

                function updateVariations() {
                    var productId = productField.val();

                    $.ajax({
                        url: '/get-variations/',
                        data: { product_id: productId, cart_item_id: currentId },
                        success: function(data) {
                            if(data.length > 0){        
                                var wrapper = variationsField;
                                wrapper.empty();                    
                                var variationsContainer = $('<div id="id_variations"></div>');

                                var checkboxes = data;
                                
                                $.each(checkboxes, function(index, checkbox) {
                                    var label = $('<label for="id_variations_' + index + '"></label>');
                                    var input = $('<input type="checkbox" name="variations" value="' + checkbox.id + '" id="id_variations_' + index + '">');
                                    
                                    if (checkbox.checked) {
                                        input.prop('checked', true);
                                    }
                                    
                                    label.append(input, ' ' + checkbox.value);
                                    variationsContainer.append($('<div></div>').append(label));
                                });

                                var addLink = $('<a class="related-widget-wrapper-link add-related" id="add_id_variations" data-popup="yes" href="/admin/store/variation/add/?_to_field=id&amp;_popup=1" title="Add another variation"></a>');
                                addLink.append($('<img src="/static/admin/img/icon-addlink.svg" alt="Add">'));

                                wrapper.append(variationsContainer);

                                $('#containerElementId').append(wrapper);
                            }else{
                                variationsField.html(data);
                            }
                        }
                    });
                }
                
                updateVariations()
                productField.on('change', updateVariations);
            }
        });
    })(django.jQuery);
});