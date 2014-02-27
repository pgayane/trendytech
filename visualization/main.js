var lang_data;
var width = window.innerWidth;
var height = window.innerHeight/2;
var lang_data;

var subwidth = window.innerWidth/2;
var subheight = window.innerHeight/2;

var axisPadding = 100;
var barPadding = 1;
var labelPadding = 10;
var barwidth;
var bottomPadding = 80;
var scale;
var prevtime = 0;
var time = 0;

window.onload = function(){

    d3.json('data.json', function(error, data){
       lang_data = data['languages'];
       init();
    });

}

function init(){
    
    barwidth = (width - axisPadding)/lang_data.length - barPadding;

    var maxValue = d3.max(lang_data, function(d){
        return d['nor'][0];
    });
    var mimValue = d3.min(lang_data, function(d){
        return d['nor'][0];
    });

    scale = d3.scale.pow();
    scale.domain([1, maxValue]);
    scale.range([height - bottomPadding, 0]);
    scale.exponent(0.5);

    createTimeline();
    createMainSVG();
    createSubSVG();
    createBars();
    createBarLabels();
};

function createMainSVG(){
    var svg = d3.select('body').append('svg')
                                .attr('id', 'mainsvg')
                                .attr('width', width)
                                .attr('height', height);

    var ys = new Array();
    for(i = 0; i < 10; i++)
    {   ys[i] = (i*i*10000);
        console.log(ys[i]);
    }
     
    yaxis = d3.svg.axis().scale(scale).orient('left')
                .tickFormat(function(d) { return d/1000 + "K"; })
                .tickValues(ys);
    svg.append('g')
        .attr("transform", "translate(100, 0)")        
        .call(yaxis);
};

function createSubSVG(){
    var svg = d3.select('body').append('svg')
                                .attr('id', 'subsvg')
                                .attr('width', subwidth)
                                .attr('height', subheight);

};

function createBars(){
    var svg = d3.select('#mainsvg');

    var rects = svg.selectAll('rect').data(lang_data);
        rects
        .enter()
        .append('rect')
        .attr('x', function(d, i){return axisPadding + i*(barwidth+barPadding);})
        .attr('y', height - bottomPadding)
        .attr('width', barwidth)
        .attr('height', 0)
        .attr('fill', 'black')
        .transition()
        .duration(1000)
        .attr('height', function(d) { 
            return height - bottomPadding - scale(d['nor'][time]);})
        .attr('y', function(d) { 
            return scale(d['nor'][time]);} )
        .each('end', function(d, i){
            d3.select(this).call(hoverData);
        });      
};

function createBarLabels(){
    var svg = d3.select('#mainsvg');
    svg.selectAll('.language')
        .data(lang_data)
        .enter()
        .append('text')
        .text(function(d) {return d['name'];})
        .attr('x', function(d, i){return axisPadding+ i*(barwidth+barPadding);})
        .attr('y', height-bottomPadding+labelPadding)
        .attr('transform', function(d, i) {
            return 'rotate(50 ' + (axisPadding + i*(barwidth+barPadding)).toString() + ' ' + (height-bottomPadding+labelPadding).toString()+")";
        });
};

function highlightBars(selection){
    selection
        .on('mouseover', function(d, i){
            x = this.getAttribute('x');
            y = this.getAttribute('y');

            d3.select(this).attr('fill', '#999');
            // d3.select('svg').append('text')
            //                 .text(d['2012'])
            //                 .attr('id', 'label')
            //                 .attr('x', x)
            //                 .attr('y', y)
            createSubBars(d);
        })
        .on('mouseout', function(){
            d3.select(this).attr('fill', 'black');
            d3.select('#label').remove();
        })

};

function createSubBars(item){
    d3.select('#subsvg').selectAll('rect').remove();

    d3.select('#subsvg').selectAll('rect').data(item['nor'])
                .enter()
                .append('rect')
                .attr('x', function(d, i){return i*(barwidth+barPadding);})
                .attr('y', subheight - bottomPadding)
                .attr('width', barwidth)
                .attr('height', 0)
                .attr('fill', 'black')
                .transition()
                .duration(1000)
                .attr('height', function(d) { return scale(d);})
                .attr('y', function(d) { return subheight -bottomPadding- scale(d);})
};


function hoverData(selection){
    highlightBars(selection);    
};

function createTimeline(){
    d3.select('body').append('input')
    .attr('type', 'range')
    .attr('min', 0)
    .attr('max', 1)
    .attr('value', 0)
    .attr("name","points")
    .on('change', function(){ 
        time = this.value;
        return transform();

    });
    
 };


 function transform(){
    updateedRects = d3.select('body').select('#mainsvg').selectAll('rect').data(lang_data);
            
    updateedRects
        .attr('x', function(d, i){return axisPadding + i*(barwidth+barPadding);})
        .attr('width', barwidth)
        .attr('height', function(d) { return height - bottomPadding - scale(d['nor'][prevtime]);})
        .attr('y', function(d) { return  scale(d['nor'][prevtime]);} )
        .attr('fill', 'black')
        .transition()
        .duration(2000)
        .attr('height', function(d) { return height - bottomPadding - scale(d['nor'][time]);})
        .attr('y', function(d) { return scale(d['nor'][time]);} )
        .each('end', function(d, i){
                d3.select(this).call(hoverData);  
        })

    prevtime = time;
 };