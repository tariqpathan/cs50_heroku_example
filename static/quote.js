$(document).ready(function() {
            
    $('#stock-search').typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: 'stocks',
        display: function(suggestion) { return null; },
        limit: 10,
        source: search,
        templates: {
            suggestion: Handlebars.compile(
                "<div>{{symbol}} - {{name}}</div>"
            ),
            pending: function() { return "<div> Searching... </div>"; },
            notFound: function() { return "<div> No results found </div>" }
        }
    });

    function search(query, syncResults, asyncResults)
    {
    // Get stocks matching query (asynchronously)
        let parameters = {
            q: query
        };
        $.getJSON("/search_stocks", parameters, function(data, textStatus, jqXHR) {

            // Call typeahead's callback with search results (i.e., places)
            asyncResults(data);
        });
    }

    $('#stock-search').on("typeahead:selected", function(object, data, name) {
        $.get("/stock_quote", {'symbol': data['symbol']}, function(result) {
            $('#results').html(result);
        });
    });

})