(function($) {
    $(document).ready(function() {
        function toggleFieldsets() {
            var blockType = $('#id_block_type').val();
            var $fieldsets = $('fieldset.module'); 
            
            // if "standard", hide dynamic (1,2,3), show html (4)
            if (blockType === 'standard') {
                $fieldsets.eq(1).hide();
                $fieldsets.eq(2).hide();
                $fieldsets.eq(3).hide();
                $fieldsets.eq(4).show();
            } else {
                // else hide html && show dynamic
                $fieldsets.eq(1).show();
                $fieldsets.eq(2).show();
                $fieldsets.eq(3).show();
                $fieldsets.eq(4).hide();
            }
        }

        $('#id_block_type').change(toggleFieldsets);
        toggleFieldsets();
    });
})(django.jQuery || jQuery);
