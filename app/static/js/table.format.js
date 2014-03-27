/**
 * Created by Josh on 1/25/14.
 */

$(document).ready(function () {
    $("#filetable_body tr").each(function () {
        console.log("Hitting JS in separate file")
        var $this_row = $(this);
        var $this_trust_cell = $(this).find("#filetrust");
        var $this_threat_cell = $(this).find("#filethreat");
        var $this_vt_cell = $(this).find("#virustotal");
        var fileTrust = $this_trust_cell.text();
        var fileThreat = $this_threat_cell.text();
        var vt = $this_vt_cell.text();
        vt = parseInt(vt.replace("%", ''));
        <!-- Trust -->
        if (!fileTrust.trim()) {
            $this_trust_cell.find("#label_span").attr('class', "label label-default");
            $this_trust_cell.find("#glyph_span").attr('class', 'glyphicon glyphicon-ban-circle');
        } else {
            if (fileTrust < 8) {
                $this_trust_cell.find("#label_span").attr('class', 'label label-warning');
                $this_trust_cell.find("#glyph_span").attr('class', 'glyphicon glyphicon-warning-sign');
            }
            if (fileTrust < 5) {
                $this_row.addClass("danger");
                $this_trust_cell.find("#label_span").attr('class', "label label-danger");
                $this_trust_cell.find("#glyph_span").attr('class', 'glyphicon glyphicon-remove');
            }
        }
        <!-- Threat -->
        if (!fileThreat.trim()) {
            $this_threat_cell.find("#label_span").attr('class', "label label-default");
            $this_threat_cell.find("#glyph_span").attr('class', 'glyphicon glyphicon-ban-circle');
        } else {
            if (fileThreat > 5) {
                $this_threat_cell.find("#label_span").attr('class', 'label label-warning');
                $this_threat_cell.find("#glyph_span").attr('class', 'glyphicon glyphicon-warning-sign');
            }
            if (fileThreat > 8) {
                $this_row.addClass("danger");
                $this_threat_cell.find("#label_span").attr('class', "label label-danger");
                $this_threat_cell.find("#glyph_span").attr('class', 'glyphicon glyphicon-remove');
            }
        }
        <!-- VirusTotal -->
        if (vt < 33) {
            $this_vt_cell.find("#vt_button").attr('class', 'btn btn-success btn-xs');
        }
        if (vt > 33) {
            $this_vt_cell.find("#vt_button").attr('class', "btn btn-warning btn-xs");
        }
        if (vt > 66) {
            $this_row.addClass("danger");
            $this_vt_cell.find("#vt_button").attr('class', "btn btn-danger btn-xs");
        }
    });
});