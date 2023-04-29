<?php
/**
 * Plugin Name: Page profiler
 * Description:
 * Version: 1.0
 */

function page_profile() {
    ob_start();
    add_action( 'shutdown', function() {
	    $html = ob_get_clean();
	    file_put_contents( '/home/jzwoo/Desktop/cs5331_page_profiler/request.txt', $html );
	    $is_safe = shell_exec( 'cd /home/jzwoo/Desktop/cs5331_page_profiler; . venv/bin/activate; python3 scripts.py' );
	    if ( $is_safe == 1 ) {
		    echo $html;
	    } else {
		    echo 'Possible unsafe scripts detected.';
	    }
    }, 0 );
}

add_action( 'template_redirect', 'page_profile' );

