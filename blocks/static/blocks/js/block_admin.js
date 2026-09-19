(function($) {
    $(document).ready(function() {
        function toggleFieldsets() {
            var blockType = $('#id_block_type').val();
            var $fieldsets = $('fieldset.module');
            var isVideo = blockType === 'videos' || $('#id_name').val() === '_Videos';
            $fieldsets.filter('.video-display-options').toggle(isVideo);

            // if "standard", hide dynamic (1,2,3), show html (4)
            if (blockType === 'standard') {
                $fieldsets.eq(1).hide();
                $fieldsets.eq(2).hide();
                $fieldsets.eq(3).hide();
                $fieldsets.eq(5).show();
            } else if (blockType === 'videos') {
                $fieldsets.eq(1).show();
                $fieldsets.eq(2).hide();
                $fieldsets.eq(3).hide();
                $fieldsets.eq(5).hide();
            } else {
                // else hide html && show dynamic
                $fieldsets.eq(1).show();
                $fieldsets.eq(2).show();
                $fieldsets.eq(3).show();
                $fieldsets.eq(5).hide();
            }
            $('#id_selected_topic, #id_selected_category').closest('.form-row').toggle(blockType !== 'videos');
            $('#id_feature_first_article, #id_exclude_duplicates, #id_display_in_columns').closest('.field-box').toggle(blockType !== 'videos');
            $('label[for="id_num_articles"]').text(blockType === 'videos' ? 'Number of videos:' : 'Num articles:');
        }

        $('#id_block_type, #id_name').on('change input', toggleFieldsets);
        toggleFieldsets();
    });
})(django.jQuery || jQuery);
