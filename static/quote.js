$(document).ready(function() {
            
    $('#stock-search').typeahead({
        minLength: 1,
        highlight: true,
        hint: true
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
            pending: function() { return "<div>Searching...</div>"; },
            notFound: function() { return "<div>None Found</div>" }
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
            console.log(data);
        });
    }

})