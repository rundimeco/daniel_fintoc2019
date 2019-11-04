<?php
$verbose = false;

$header = '<bs-submission participant-id="groundtruth" run-id="gl-1" task="book-toc" toc-creation="manual" toc-source="full-content"><source-files pdf="yes" xml="no" /><description>This file contains a run made by Giguet-Lejeune.</description>';


if (!function_exists('array_key_first')) {
  function array_key_first(array $arr) {
    foreach($arr as $key => $unused) {
      return $key;
    }
    return NULL;
  }
}
if (! function_exists("array_key_last")) {
  function array_key_last($array) {
    if (!is_array($array) || empty($array)) {
      return NULL;
    }
       
    return array_keys($array)[count($array)-1];
  }
}

$filename = $_SERVER['argv'][1];

if (!is_dir($filename)) {
  if (preg_match('~\.pdf$~i',$filename))
    $filename = basename(preg_replace('~\.pdf$~i','.xml_data',$filename));
}

if (is_dir($filename)) {
  if (($filenames = glob($filename.DIRECTORY_SEPARATOR.'pageNum-*.xml')) === false) {
    die('No XML Page File in Directory.');
  }
}

$numPages = count($filenames);
// echo $numPages." pages\n";


// Mise en correspondance de la numérotation des pages

$searchRange = range(1,10);
$pages = array();
foreach($searchRange as $pageNum) {
  $pagefilename = $filename.DIRECTORY_SEPARATOR.'pageNum-'.$pageNum.'.xml';
  if (($content = file_get_contents($pagefilename)) == false) continue;

  $targetPages = isset($_SERVER['argv'][2]) ? $_SERVER['argv'][2] : false;

  $ntok = preg_match_all('~<TOKEN([^<>]*)>(\d\d?)</TOKEN>~',$content,$m_tokens);

  $attrs = array();
  foreach($m_tokens[2] as $i=> $tok) {
    preg_match_all('~([a-z-]+)="(.*?)"~',$m_tokens[1][$i],$m_attrs);
    $tok_attrs = array_combine($m_attrs[1],$m_attrs[2]);
    $attrs[] = $tok_attrs;
  }

  foreach($m_tokens[2] as $i=> $tok) {
    if ($tok > 10) continue;
    $coord = intval($attrs[$i]['x']).'-'.intval($attrs[$i]['y']);
    if (!isset($pages[$coord])) $pages[$coord] = array();
    $pages[$coord][] = $pageNum.'-'.$tok;
  }
  
  uasort($pages,function($a,$b) { return count($b) - count($a); });
}
$pagemap = current($pages);
$firstPageMap = explode('-',$pagemap[0]);
$decPage = $firstPageMap[0] - $firstPageMap[1];




// Espace de recherche en début de document
$searchRange = range(1,intval($numPages/3));

// Arrêt de la recherche après avoir identifié la TOC, éventuellement sur plusieurs pages contigues

$xml = '';
$tocLocationFound = false;
foreach($searchRange as $pageNum) {
  $pagefilename = $filename.DIRECTORY_SEPARATOR.'pageNum-'.$pageNum.'.xml';
  if (($response = parse($pagefilename, $verbose)) === false && $tocLocationFound) break;
  $xml .= $response['xml'];
  $tocLocationFound |= $response !== false;
}


if ($xml == '') {

$searchRange = range(1,$numPages);
$lines = array();
foreach($searchRange as $pageNum) {
  $pagefilename = $filename.DIRECTORY_SEPARATOR.'pageNum-'.$pageNum.'.xml';
  if (($content = file_get_contents($pagefilename)) == false) continue;

  $targetPages = isset($_SERVER['argv'][2]) ? $_SERVER['argv'][2] : false;

  $ntext = preg_match_all('~<TEXT([^<>]*)>(.*?)</TEXT>~',$content,$m_tokens);

  $attrs = array();
  foreach($m_tokens[2] as $i=> $tok) {
    preg_match_all('~([a-z-]+)="(.*?)"~',$m_tokens[1][$i],$m_attrs);
    $tok_attrs = array_combine($m_attrs[1],$m_attrs[2]);
    $attrs[] = $tok_attrs;
  }

  foreach($m_tokens[2] as $i=> $tok) {
    $lines[] = array($pageNum,preg_replace('~(<[^<>]*>)+~',' ',$tok));
  }
}
$lines = array_filter($lines,function($line) { return preg_match('~^ \d+\.\s~',$line[1]); });

$lines = array_map(function($line) { 
    list($page,$title) = $line;
    $title = trim($title);
   return '<toc-entry matter_attrib="body" page="'.$page.'" title="'.$title.'"></toc-entry>';
  },$lines);
$xml = join("\n",$lines);
}

echo '<book>'."\n".'<bookid>'.str_replace('.xml_data','.pdf',$filename).'</bookid>'."\n";
echo $xml;
echo '</book>';


function parse($filename, $verbose = false) {

  global $decPage;

  $content = file_get_contents($filename);

  $targetPages = isset($_SERVER['argv'][2]) ? $_SERVER['argv'][2] : false;


  $ntok = preg_match_all('~<TOKEN(.*?)>(.*?)</TOKEN>~',$content,$m_tokens);
  if ($verbose) {
    echo $ntok." tokens.\n";
  }

  // echo join("\n",$m_tokens[2]);
  // echo "\n\n";

  // 1. Parse and Map Token Attributes;

  $attrs = array();
  foreach($m_tokens[2] as $i=> $tok) {
    preg_match_all('~([a-z-]+)="(.*?)"~',$m_tokens[1][$i],$m_attrs);
    $tok_attrs = array_combine($m_attrs[1],$m_attrs[2]);
    $attrs[] = $tok_attrs;
  }

  // 2. Build lines

  $cury = 0;   // current y offset
  $lines = []; // table of lines
  $line = [];

  $hspans = array(); // Horizontal span
  $right = $attrs[1]['x'];
  foreach($m_tokens[2] as $i=> $tok) {
    // echo '{'.$attrs[$i]['y'].','.$attrs[$i]['x'].'}'.$tok."\n";
    if (abs($cury - $attrs[$i]['y']) > 2  && count($line) > 0) { $hspans[] = array($right,$left); $lines[] = $line; $line=[]; $right = $attrs[$i]['x'] ;$cury = $attrs[$i]['y'] ; }
    $line[] = $tok;
    $left = $attrs[$i]['x'] + $attrs[$i]['width'];
  }
  $hspans[] = array($right,$left);
  $lines[] = $line;

  // Todo : Reorder lines

  // Display Lines
  //array_map(function($line) { echo join(' ',$line)."\n"; }, $lines);
  // Display Line Horizontal Span
  //array_map(function($hspan) { echo join('-',$hspan)."\n"; },$hspans);

  // 3. Compute End By Right Aligned Number Lines

  // 3.1 Filter lines ending by numbers (i.e, integers, not float)

  $endByNumberLines = array_filter($lines,function($line) { $lastToken = count($line) > 0 ? $line[count($line)-1] : '' ; return preg_match('~\d+$~',$lastToken) && !preg_match('~\d+[.,]\d+$~',$lastToken); });

  // 3.2 Compute End Of Line Distribution

  $rights = array_map(function($hspan) { return ''.round($hspan[1],1); },$hspans);
  $count_right_pos = array_count_values($rights);
  arsort($count_right_pos);

  // 3.3 Extract Most Frequent EOL Position and Corresponding Lines

  $most_frequent_right_pos = each($count_right_pos)[0];
  $right_aligned = array_filter($hspans,function($hspan) use ($most_frequent_right_pos) { return abs($hspan[1]-$most_frequent_right_pos) < 1; });

  // 3.4 Intersect Lines Ending by Numbers and Most Frequent Right Aligned Lines

  $right_aligned_numbered_lines = array_intersect_key($endByNumberLines,$right_aligned);

  if ($verbose) {
    echo "---- End By Right Aligned Number ----\n";
    array_map(function($line) { echo join(' ',$line)."\n"; }, $right_aligned_numbered_lines);
    echo "\n\n";
  }

  // $max_span_in_toc_line = array_map(function($hspan) { return ''.round($hspan[1]-$hspan[0],1); },   );

  $first_line = array_key_first($right_aligned_numbered_lines);
  $last_line = array_key_last($right_aligned_numbered_lines);

  // Select Lines for Tables Of Contents

  $toc = array_slice($lines,$first_line, $last_line - $first_line + 1, true);

  if ($verbose) {
    echo "---- Selected Lines for Tables Of Contents ----\n";
    array_map(function($line) { echo join(' ',$line)."\n"; }, $toc);
    echo "\n\n";
  }


  $numberedLinesInTOC = count(array_intersect_key($toc,$right_aligned_numbered_lines)) / count($toc);
  if ($numberedLinesInTOC < 0.75 || count($toc) < 5) {
    return false;
  }

  // 4. Infer Hierarchical Structure From Indentation

  // 4.1 Extract Indentation Position for Toc Lines

  $precision = 1;
  $hspansOfToc = array_intersect_key($hspans,$toc);
  $lefts = array_map(function($hspan) use ($precision) { return ''.round($hspan[0],$precision); },$hspansOfToc);

  // Count lines starting at same position
  $compact_lefts = array_count_values($lefts);
  // Count lines starting at similar position
  $compact_lefts_pos = array_keys($compact_lefts);
  sort($compact_lefts_pos);
  foreach($compact_lefts_pos as $i => $p) {
    if ($i == 0) continue;
    $diff = $p - $compact_lefts_pos[$i-1];
    if (abs($diff) > 1) continue;

    $diff = $compact_lefts[$p] - $compact_lefts[$compact_lefts_pos[$i-1]];

    if ($diff >= 0) {
      $compact_lefts[$p] += $compact_lefts[$compact_lefts_pos[$i-1]];
      unset($compact_lefts[$compact_lefts_pos[$i-1]]);
    }
    else {
      $compact_lefts[$compact_lefts_pos[$i-1]] += $compact_lefts[$p];
      unset($compact_lefts[$p]);
    }
  }
  // Keep representative starting position
  $compact_lefts = array_filter($compact_lefts,function($count) { return $count > 2; });
  ksort($compact_lefts);
  // Map position to level
  $mapPos2Level = array_flip(array_keys($compact_lefts));

  $indentation_infer = count($mapPos2Level) >= 2;
  if ($verbose) {
    print_r($mapPos2Level);
  }
  $indent_line2Levels = array_map(function($hspan) use ($mapPos2Level,$precision) { return isset($mapPos2Level[''.round($hspan[0],$precision)]) ? $mapPos2Level[''.round($hspan[0],$precision)] : false; }, $hspansOfToc);

  if ($verbose && $indentation_infer === true) {  
    echo "---- Infered Hierarchy From Indentation ----\n";
    array_map(function($level,$line) { echo ''.($level === false ? '?' : str_pad('',5*$level,' ' )).join(' ',$line)."\n"; }, $indent_line2Levels, $toc);
    echo "\n\n";
  }

  // 5. Infer Hierarchical Structure From Level Numbering

  $number_line2Levels = array_map(function($line) { $match_numbering = preg_match('~^(?:(\d+|[A-Z]|[ivx]+)[./:) -])+~i',join(' ',$line),$m_numparts); $level = $match_numbering ? count(preg_split('~[./:) -]~',$m_numparts[0],-1,PREG_SPLIT_NO_EMPTY)) - 1 : false ; return $level; }, $toc );
  // print_r($number_line2Levels);

  if ($verbose && $indentation_infer === false) {
    echo "---- Infered Hierarchy From Section Numbering ----\n";
    array_map(function($level,$line) { echo ''.($level === false ? '?' : str_pad('',5*$level,' ' )).join(' ',$line)."\n"; }, $number_line2Levels, $toc);
    echo "\n\n";
  }

  $combined_infer = array_map(function($indent, $level) { if ($level === false) return $indent; if ($indent === false) return $level; return max($indent,$level); }, $indent_line2Levels, $number_line2Levels);

  $text = array_map(function($level,$line) { return ''.($level === false ? '?' : str_pad('',5*$level,' ' )).join(' ',$line); }, $combined_infer, $toc);
  // echo join("\n",$text);
  
  $xml = '';
  ob_start();
  $depth = array();
  $page = 1;
  array_map(function($level,$line) use (&$depth,&$page,$decPage) { 
      $line = join(' ',$line);
      if (preg_match('~\d+$~',$line,$m_page)) {
	$page = $m_page[0];
	$title = preg_replace("~(\. ?)*$page$~",'',$line);
	$page += $decPage;
      }      
      else {
	$title = preg_replace("~(\. ?)*$~",'',$line);
      }
      $title = trim($title);

      $entry = '<toc-entry matter_attrib="body" page="'.$page.'" title="'.$title.'">';
      if (count($depth) == 0) { echo $entry."\n"; $depth[] = $level;}
      elseif ($level == end($depth)) { echo "</toc-entry>"."\n".$entry."\n"; }
      elseif ($level > end($depth)) { $depth[] = $level ; echo $entry."\n"; }
      elseif ($level < end($depth)) { for(;count($depth) > 0 && end($depth) != $level ; array_pop($depth)) { echo "</toc-entry>"."\n"; }; echo "</toc-entry>"."\n";  echo $entry."\n"; }
      
    }, $combined_infer, $toc);
  for (;count($depth) > 0 ;array_pop($depth) ) { echo '</toc-entry>'."\n"; } 
  $xml = ob_get_clean();

  return array('infer' => $combined_infer, 'xml' => $xml, 'txt' => $text);
}


 exit(0);
$cury = 0;
$toky = array();
foreach($m_tokens[2] as $i=> $tok) {
  if ($cury != $attrs[$i]['y'] || ($cury < $attrs[$i]['y'])) { $cury = $attrs[$i]['y'] ; $toky = array();}
  $toky[] = $tok;
  $isDotLeaderCandidate = preg_match('~([^\.]*)\.\.+$~',$tok) ||
            preg_match('~\.\.+\d+$~',$tok);
  // echo '{'.$attrs[$i]['y'].'}'.$tok.' '.($isDotLeaderCandidate ? 'yes':'no')."\n";
  $isPageNumberCandidate = isset($m_tokens[1][$i+1]) && (preg_match('~(\d+)~',$m_tokens[1][$i+1],$m_page) ||
							 preg_match('~(?:[^\.]*)\.\.+(\d)+$~',$tok,$m_page));
  if ($isDotLeaderCandidate && $isPageNumberCandidate) {
    $dots = $tok;
    $page = $m_page[1];
    echo join(' ',$toky) ." $page\n";
  }
}


